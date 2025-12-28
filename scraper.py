import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def run_proprietary_engine():
    async with async_playwright() as p:
        # We launch with 'stealth' settings
        browser = await p.chromium.launch(headless=True)
        
        # We define a very specific 'human' context
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0",
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            locale="en-US",
            timezone_id="America/Chicago"
        )
        
        # Add 'Stealth' scripts to the page to hide Playwright variables
        page = await context.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)
        
        all_events = []
        
        for i in range(1, 6):
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"Ghost Scanning Page {i}...")
            
            try:
                # Go to page and wait for a specific element that proves the data loaded
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Human-like delay and scroll
                await asyncio.sleep(4)
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(2)

                # Look for the LEARN MORE buttons we know should be there
                items = await page.query_selector_all(".listing-item, .item")
                
                page_count = 0
                for item in items:
                    title_el = await item.query_selector("h3, .title, .listing-title")
                    link_el = await item.query_selector("a")
                    
                    if title_el and link_el:
                        title = await title_el.inner_text()
                        href = await link_el.get_attribute("href")
                        if href and "/view/" in href:
                            all_events.append({
                                "id": href.split("/")[-1],
                                "title": title.strip(),
                                "url": f"https://www.travelok.com{href}" if href.startswith("/") else href
                            })
                            page_count += 1
                
                print(f"Page {i}: Successfully found {page_count} events.")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:50]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['id'])
            df.to_csv("master.csv", index=False)
            print(f"Total: {len(df)} events saved.")
        else:
            # Last ditch: what is the actual text now?
            text = await page.inner_text("body")
            print(f"Text length: {len(text)}. First 200 chars: {text[:200]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
