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
            print(f"Surgical Scan Page {i}: {url}")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait for the specific text we saw in your log
                try:
                    await page.wait_for_selector("text=LEARN MORE", timeout=15000)
                except:
                    print(f"Timeout waiting for 'LEARN MORE' on page {i}")

                # Extraction Logic:
                # Based on the text log, events are grouped. 
                # We will find all 'LEARN MORE' links and their surrounding titles.
                listings = await page.query_selector_all("//div[contains(@class, 'listing')] | //div[contains(@class, 'item')]")
                
                page_count = 0
                for item in listings:
                    # Look for the title (usually a heading or bold text above LEARN MORE)
                    title_el = await item.query_selector("h3, .listing-title, .title")
                    link_el = await item.query_selector("a:has-text('LEARN MORE'), a.btn, .learn-more a")
                    
                    if title_el and link_el:
                        title_text = await title_el.inner_text()
                        href = await link_el.get_attribute("href")
                        
                        if href:
                            clean_url = "https://www.travelok.com" + href if href.startswith("/") else href
                            all_events.append({
                                "id": href.split("/")[-1],
                                "title": title_text.strip(),
                                "url": clean_url
                            })
                            page_count += 1
                
                # Fallback: If the structured search fails, just grab EVERY link that says LEARN MORE
                if page_count == 0:
                    backup_links = await page.query_selector_all("a:has-text('LEARN MORE')")
                    for link in backup_links:
                        href = await link.get_attribute("href")
                        # Look for a title nearby (the previous sibling or parent's heading)
                        title_text = await page.evaluate("(el) => el.parentElement.parentElement.querySelector('h3, .title')?.innerText", link)
                        
                        if href:
                            clean_url = "https://www.travelok.com" + href if href.startswith("/") else href
                            all_events.append({
                                "id": href.split("/")[-1],
                                "title": title_text.strip() if title_text else "Event",
                                "url": clean_url
                            })
                            page_count += 1

                print(f"Captured {page_count} events from Page {i}")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:100]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['url'])
            df.to_csv("master.csv", index=False)
            print(f"Final Count: {len(df)} unique events saved.")
        else:
            print("Extraction failed. The elements are likely inside a Shadow DOM.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
