import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import random

async def run():
    async with async_playwright() as p:
        # Launch with 'Stealth' arguments
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        # Use a real browser's "Identity Card" (User Agent)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        results = []
        for i in range(1, 11): # Start with just 10 pages to test stability
            print(f"Human-mimic scraping Page {i}...")
            try:
                # Add a random delay so we don't look like a machine (1 to 4 seconds)
                await asyncio.sleep(random.uniform(1, 4)) 
                
                await page.goto(f"https://www.travelok.com/listings/search/15?page={i}", wait_until="networkidle")
                
                # Check if the events actually appeared
                await page.wait_for_selector(".listing-item", timeout=15000)
                
                items = await page.query_selector_all(".listing-item")
                for item in items:
                    results.append({
                        "id": await item.get_attribute("data-id"),
                        "title": await (await item.query_selector(".listing-title")).inner_text(),
                    })
            except Exception as e:
                print(f"Page {i} failed or timed out. Moving on.")
        
        pd.DataFrame(results).to_csv("master.csv", index=False)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
