import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

async def run_proprietary_engine():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0"
        )
        page = await context.new_page()
        
        all_events = []
        
        for i in range(1, 6):
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"Deep Scanning Page {i}: {url}")
            
            try:
                # Load and wait for the page to settle
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Force a scroll to trigger any dynamic loading
                await page.mouse.wheel(0, 2000)
                await asyncio.sleep(4)
                
                if i == 1:
                    await page.screenshot(path="debug_screenshot.png")

                # PROPRIETARY SCAN: Find every link on the page
                links = await page.query_selector_all("a")
                
                page_count = 0
                for link in links:
                    href = await link.get_attribute("href")
                    text = await link.inner_text()
                    
                    # We only care about links that go to /listings/view/
                    if href and "/listings/view/" in href:
                        # Use the URL as a unique ID to avoid duplicates
                        clean_url = "https://www.travelok.com" + href if href.startswith("/") else href
                        
                        # Only add if it has a title (skips empty icon links)
                        if text and len(text.strip()) > 2:
                            all_events.append({
                                "id": href.split("/")[-1], # Gets the ID from the end of the URL
                                "title": text.strip(),
                                "url": clean_url
                            })
                            page_count += 1
                
                print(f"Found {page_count} potential event links on Page {i}")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:100]}")

        if all_events:
            # Clean up duplicates
            df = pd.DataFrame(all_events).drop_duplicates(subset=['url'])
            df.to_csv("master.csv", index=False)
            print(f"Final Totals: {len(df)} unique events saved to master.csv")
        else:
            # If this fails, we will print the full text of the page to see what's there
            print("Deep Scan found nothing. Extracting page text for diagnostic:")
            page_text = await page.evaluate("document.body.innerText")
            print(page_text[:1000])
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
