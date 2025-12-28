import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os

async def get_details(context, url):
    page = await context.new_page()
    try:
        await page.goto(url, timeout=15000)
        # Targeted selectors for organizer info
        organizer = await page.query_selector(".listing-contact")
        text = await organizer.inner_text() if organizer else "No Info"
        await page.close()
        return text.strip()
    except:
        await page.close()
        return "N/A"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        
        results = []
        for i in range(1, 51): # Hits 50 pages (approx 1000 records)
            print(f"Scraping Page {i}...")
            await page.goto(f"https://www.travelok.com/listings/search/15?page={i}")
            await page.wait_for_selector(".listing-item")
            
            items = await page.query_selector_all(".listing-item")
            for item in items:
                link_el = await item.query_selector("a.listing-btn")
                link = "https://www.travelok.com" + await link_el.get_attribute("href")
                
                results.append({
                    "id": await item.get_attribute("data-id"),
                    "title": await (await item.query_selector(".listing-title")).inner_text(),
                    "date": await (await item.query_selector(".listing-date")).inner_text(),
                    "img": await (await item.query_selector("img")).get_attribute("src"),
                    "organizer": await get_details(context, link) # Deep scrape
                })
        
        df_new = pd.DataFrame(results)
        # Diff Logic (New vs Deleted)
        if os.path.exists("master.csv"):
            df_old = pd.read_csv("master.csv")
            df_new[~df_new['id'].isin(df_old['id'])].to_csv("NEW_EVENTS.csv", index=False)
            df_old[~df_old['id'].isin(df_new['id'])].to_csv("DELETED_EVENTS.csv", index=False)
        
        df_new.to_csv("master.csv", index=False)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
