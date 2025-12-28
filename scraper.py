import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # 1. Launch with extra arguments to look like a real PC
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        results = []
        # Let's test just Page 1 and Page 2 first to ensure it's working
        for i in range(1, 3): 
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"Attempting to scrape: {url}")
            
            try:
                # Increased timeout and 'networkidle' to ensure JS loads
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Check if we got blocked
                content = await page.content()
                if "Access Denied" in content or "Cloudflare" in content:
                    print(f"⚠️ BLOCKED by website security on page {i}")
                    continue

                # Wait for the specific event cards
                await page.wait_for_selector(".listing-item", timeout=15000)
                items = await page.query_selector_all(".listing-item")
                
                print(f"Found {len(items)} items on page {i}")
                
                for item in items:
                    title_el = await item.query_selector(".listing-title")
                    results.append({
                        "id": await item.get_attribute("data-id"),
                        "title": await title_el.inner_text() if title_el else "N/A",
                    })
            except Exception as e:
                print(f"❌ Error on page {i}: {str(e)}")
        
        if results:
            df = pd.DataFrame(results)
            df.to_csv("master.csv", index=False)
            print(f"✅ Success! Saved {len(results)} records to master.csv")
        else:
            print("⚠️ No data found. master.csv will remain empty.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
