import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

# Use your ScrapingAnt API Key
API_KEY = os.getenv("ANT_KEY")

async def run_proprietary_engine():
    if not API_KEY:
        print("Error: ANT_KEY not found in Environment Variables")
        return

    async with async_playwright() as p:
        # We connect to a proxy server instead of a local browser
        # This makes the request look like it is coming from a real home in the US
        proxy_url = f"http://{API_KEY}:@proxy.scrapingant.com:8080"
        
        browser = await p.chromium.launch(
            proxy={"server": proxy_url}
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0"
        )
        page = await context.new_page()
        
        all_events = []
        
        for i in range(1, 6):
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"Proxy Scanning Page {i}...")
            
            try:
                # The proxy handles the 'stealth' part for us
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait for the data to mount
                await page.wait_for_selector(".listing-item", timeout=20000)
                
                items = await page.query_selector_all(".listing-item")
                page_count = 0
                
                for item in items:
                    title_el = await item.query_selector("h3, .listing-title")
                    link_el = await item.query_selector("a")
                    
                    if title_el and link_el:
                        title = await title_el.inner_text()
                        href = await link_el.get_attribute("href")
                        
                        all_events.append({
                            "id": href.split("/")[-1] if href else "N/A",
                            "title": title.strip(),
                            "url": f"https://www.travelok.com{href}" if href.startswith("/") else href
                        })
                        page_count += 1
                
                print(f"Page {i}: Successfully found {page_count} events via Proxy.")
                
            except Exception as e:
                print(f"Page {i} failed via Proxy: {str(e)[:50]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['id'])
            df.to_csv("master.csv", index=False)
            print(f"Success: {len(df)} total events saved.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
