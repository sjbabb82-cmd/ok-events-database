import asyncio
import pandas as pd
import os
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
            print(f"Scanning Page {i}...")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait for at least one listing to appear
                await page.wait_for_selector("a:has-text('LEARN MORE')", timeout=10000)

                # Find every container that holds an event
                # TravelOK uses 'listing-item' as the main wrapper
                containers = await page.query_selector_all(".listing-item")
                
                page_count = 0
                for box in containers:
                    # Within this specific box, find the title and link
                    title_el = await box.query_selector("h3, .listing-title, .title")
                    link_el = await box.query_selector("a:has-text('LEARN MORE')")
                    
                    if title_el and link_el:
                        title_text = await title_el.inner_text()
                        href = await link_el.get_attribute("href")
                        
                        if href and "/view/" in href:
                            clean_url = "https://www.travelok.com" + href if href.startswith("/") else href
                            all_events.append({
                                "id": href.split("/")[-1],
                                "title": title_text.strip(),
                                "url": clean_url
                            })
                            page_count += 1

                # FALLBACK: If containers weren't found, find all LEARN MORE links directly
                if page_count == 0:
                    links = await page.query_selector_all("a:has-text('LEARN MORE')")
                    for link in links:
                        href = await link.get_attribute("href")
                        # Look 'up' from the link to find the nearest header
                        title_text = await page.evaluate("(el) => el.closest('.listing-item, div').querySelector('h3, .title, .listing-title')?.innerText", link)
                        
                        if href and "/view/" in href:
                            clean_url = "https://www.travelok.com" + href if href.startswith("/") else href
                            all_events.append({
                                "id": href.split("/")[-1],
                                "title": title_text.strip() if title_text else "Event",
                                "url": clean_url
                            })
                            page_count += 1
                
                print(f"Page {i}: Captured {page_count} events")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:50]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['url'])
            df.to_csv("master.csv", index=False)
            print(f"Success: {len(df)} total unique events saved.")
        else:
            print("Failed to find any events. Check debug screenshot.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
