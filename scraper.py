import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

async def run_proprietary_engine():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        all_events = []
        
        for i in range(1, 6):
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"Engine visiting: {url}")
            
            try:
                # Go to page
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Scroll down to trigger all lazy-loading images and data
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                await asyncio.sleep(2)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)
                
                if i == 1:
                    await page.screenshot(path="debug_screenshot.png")

                # New Discovery Logic: Look for anything that looks like a listing title
                # We target multiple possible class names used by TravelOK
                selectors = [
                    ".listing-item", 
                    ".list-item", 
                    ".item-content", 
                    "[class*='listing-item']"
                ]
                
                items = []
                for selector in selectors:
                    items = await page.query_selector_all(selector)
                    if items:
                        print(f"Discovery: Found items using selector: {selector}")
                        break

                if not items:
                    print(f"Warning: No items discovered on Page {i}")
                    continue
                
                for item in items:
                    title_el = await item.query_selector(".listing-title, h3, .title")
                    link_el = await item.query_selector("a")
                    
                    if title_el:
                        title_text = await title_el.inner_text()
                        link_href = await link_el.get_attribute("href") if link_el else ""
                        event_id = await item.get_attribute("data-id") or title_text
                        
                        all_events.append({
                            "id": event_id,
                            "title": title_text.strip(),
                            "url": f"https://www.travelok.com{link_href}" if link_href.startswith("/") else link_href
                        })
                
                print(f"Successfully captured {len(items)} events from Page {i}")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:100]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['id'])
            df.to_csv("master.csv", index=False)
            print(f"Mission Success: {len(df)} unique records saved to master.csv")
        else:
            print("Mission Failed: No events were extracted despite the page loading.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
