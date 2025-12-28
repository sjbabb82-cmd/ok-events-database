import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

async def run_proprietary_engine():
    async with async_playwright() as p:
        # Launching the browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0"
        )
        page = await context.new_page()
        
        all_events = []
        
        # Testing with first 5 pages
        for i in range(1, 6):
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"🕵️ Engine visiting: {url}")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Take a screenshot of Page 1 to verify what the robot sees
                if i == 1:
                    await page.screenshot(path="debug_screenshot.png")
                    print("📸 Screenshot saved as debug_screenshot.png")

                # Wait for the listings to actually load in the browser
                await page.wait_for_selector(".listing-item", timeout=15000)
                
                items = await page.query_selector_all(".listing-item")
                for item in items:
                    title_el = await item.query_selector(".listing-title")
                    title = await title_el.inner_text() if title_el else "N/A"
                    
                    all_events.append({
                        "id": await item.get_attribute("data-id"),
                        "title": title.strip(),
                        "url": "https://www.travelok.com" + await (await item.query_selector("a")).get_attribute("href")
                    })
                
                print(f"✅ Found {len(items)} events on Page {i}")
                
            except Exception as e:
                print(f"❌ Error on Page {i}: {str(e)[:100]}")

        # Save to CSV
        if all_events:
            pd.DataFrame(all_events).to_csv("master.csv", index=False)
            print(f"📊 Final Count: {len(all_events)} items saved to master.csv")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
