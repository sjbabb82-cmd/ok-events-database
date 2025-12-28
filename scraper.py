import asyncio
import os
from playwright.async_api import async_playwright
import pandas as pd

async def scrape():
    async with async_playwright() as p:
        # Connect to the remote browser
        browser_url = os.getenv("BROWSER_WS_ENDPOINT")
        browser = await p.chromium.connect_over_cdp(browser_url)
        
        # Set a realistic window size to trigger desktop layout
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        print("Navigating...")
        await page.goto("https://www.travelok.com/listings/search/15", wait_until="networkidle")

        # Force scroll to trigger the lazy-load data injection
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(5) 

        # Target the specific event links
        selector = "a[href*='/listings/view/']"
        try:
            await page.wait_for_selector(selector, timeout=15000)
            elements = await page.query_selector_all(selector)
            
            data = []
            for el in elements:
                title = await el.inner_text()
                link = await el.get_attribute("href")
                if title and link:
                    data.append({
                        "Title": title.strip(),
                        "URL": f"https://www.travelok.com{link}" if link.startswith('/') else link
                    })

            if data:
                df = pd.DataFrame(data).drop_duplicates()
                df.to_csv("master.csv", index=False)
                print(f"Success: {len(df)} events captured.")
            else:
                print("No data found on page.")
        except Exception as e:
            print(f"Error during extraction: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
