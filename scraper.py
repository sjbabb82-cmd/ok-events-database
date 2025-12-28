import asyncio
import os
from playwright.async_api import async_playwright
import pandas as pd

async def scrape():
    async with async_playwright() as p:
        browser_url = os.getenv("BROWSER_WS_ENDPOINT")
        browser = await p.chromium.connect_over_cdp(browser_url)
        page = await browser.new_page()

        await page.goto("https://www.travelok.com/listings/search/15", wait_until="networkidle")
        
        # This selector is the absolute minimum needed to find event links
        selector = "a[href*='/listings/view/']"
        await page.wait_for_selector(selector, timeout=30000)
        
        elements = await page.query_selector_all(selector)
        data = []
        for el in elements:
            title = await el.inner_text()
            link = await el.get_attribute("href")
            if title and link:
                data.append({"Title": title.strip(), "URL": f"https://www.travelok.com{link}"})

        pd.DataFrame(data).drop_duplicates().to_csv("master.csv", index=False)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
