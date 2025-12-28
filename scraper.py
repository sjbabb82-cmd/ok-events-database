import asyncio
import pandas as pd
import re
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
            print(f"Regex Scanning Page {i}...")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # Wait for the text we know exists from your previous log
                await page.wait_for_selector("text=LEARN MORE", timeout=20000)
                
                # Get the entire raw HTML as a string
                raw_html = await page.content()
                
                # Find all URLs matching the travelok listing pattern
                # Pattern: /listings/view/anything-here/number
                found_links = re.findall(r'/listings/view/[a-zA-Z0-9\-/]+/\d+', raw_html)
                
                page_count = 0
                for link in set(found_links): # set() removes duplicates on the same page
                    event_id = link.split('/')[-1]
                    # We create a placeholder title because title extraction 
                    # from raw HTML regex is unreliable. We will fix titles later.
                    all_events.append({
                        "id": event_id,
                        "title": f"Event {event_id}", 
                        "url": f"https://www.travelok.com{link}"
                    })
                    page_count += 1
                
                print(f"Page {i}: Found {page_count} links via Regex.")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:50]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['url'])
            df.to_csv("master.csv", index=False)
            print(f"Success: {len(df)} unique URLs saved.")
        else:
            print("Regex scan found nothing. Website may be obfuscating URLs.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
