import asyncio
import pandas as pd
import json
from playwright.async_api import async_playwright

async def run_proprietary_engine():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0"
        )
        page = await context.new_page()
        
        all_events = []

        # This function runs every time the website requests data
        async def handle_response(response):
            # We are looking for any background request that looks like a search or API
            if "search" in response.url or "listings" in response.url:
                if "json" in response.headers.get("content-type", ""):
                    try:
                        data = await response.json()
                        # Extract events from the JSON structure
                        # Modern sites often wrap results in 'data' or 'items'
                        items = data.get('data', []) if isinstance(data, dict) else []
                        for item in items:
                            all_events.append({
                                "id": item.get('id'),
                                "title": item.get('title') or item.get('name'),
                                "url": f"https://www.travelok.com/listings/view/{item.get('slug')}/{item.get('id')}"
                            })
                    except:
                        pass

        # Tell the page to use our interceptor
        page.on("response", handle_response)

        for i in range(1, 6):
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"Intercepting Data on Page {i}...")
            
            try:
                # Navigating triggers the background requests
                await page.goto(url, wait_until="networkidle", timeout=60000)
                # Wait a few seconds for all background APIs to finish
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:50]}")

        # If the API interception failed, we use a "JSON-in-HTML" extractor
        if not all_events:
            print("API Interception quiet. Searching for embedded JSON script tags...")
            content = await page.content()
            # Many sites hide their data inside a <script id="__NEXT_DATA__"> or similar
            json_blobs = await page.query_selector_all("script[type='application/json'], script[id*='data']")
            for blob in json_blobs:
                try:
                    text = await blob.inner_text()
                    if "listings" in text or "results" in text:
                        # Logic to parse this specific blob would go here
                        print("Found a potential data blob in the HTML.")
                except:
                    pass

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['id'])
            df.to_csv("master.csv", index=False)
            print(f"Success: {len(df)} events captured via Network Interception.")
        else:
            print("Final Attempt: Using the diagnostic text to force-build a CSV.")
            # We'll try to parse the raw text we saw earlier as a last resort
            raw_text = await page.evaluate("document.body.innerText")
            # Logic here would use line-by-line parsing if all else fails
            print("No structured data found. Reviewing raw text length:", len(raw_text))
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
