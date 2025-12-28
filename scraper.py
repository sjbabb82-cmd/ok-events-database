import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

# This matches the Secret name in your GitHub YAML
BROWSER_WS_ENDPOINT = os.getenv("BROWSER_WS_ENDPOINT")

async def run_premium_engine():
    if not BROWSER_WS_ENDPOINT:
        print("Error: BROWSER_WS_ENDPOINT not found. Check GitHub Secrets.")
        return

    async with async_playwright() as p:
        print("Connecting to Browserless.io remote browser...")
        
        # Connect to the high-trust remote browser
        try:
            browser = await p.chromium.connect_over_cdp(BROWSER_WS_ENDPOINT)
        except Exception as e:
            print(f"Failed to connect to remote browser: {e}")
            return

        context = await browser.new_context()
        page = await context.new_page()
        
        all_events = []
        
        # We'll scan 5 pages to start
        for i in range(1, 6):
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"Scanning Page {i}...")
            
            try:
                # Browserless handles the JavaScript and waits for the page to be ready
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # JAVASCRIPT EXTRACTION: This runs INSIDE the remote browser
                # It looks for the event cards and pulls Title, Date, and Location
                extracted = await page.evaluate("""
                    () => {
                        const items = Array.from(document.querySelectorAll('.listing-item, .card, a[href*="/view/"]'));
                        return items.map(el => {
                            const link = el.tagName === 'A' ? el : el.querySelector('a[href*="/view/"]');
                            if (!link) return null;
                            
                            // Try to find text blocks near the link
                            const container = el.closest('.listing-item') || el.parentElement;
                            return {
                                href: link.getAttribute('href'),
                                title: link.innerText || "Unknown Event",
                                info: container ? container.innerText.replace(/\\n/g, ' | ') : ""
                            };
                        }).filter(x => x !== null && x.href.includes('/view/'));
                    }
                """)
                
                for item in extracted:
                    event_id = item['href'].split('/')[-1]
                    all_events.append({
                        "id": event_id,
                        "title": item['title'].strip().split('|')[0][:100],
                        "details": item['info'][:200], # Grab a snippet of the date/location
                        "url": f"https://www.travelok.com{item['href']}" if item['href'].startswith("/") else item['href']
                    })
                
                print(f"Page {i}: Found {len(extracted)} potential entries.")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:100]}")

        if all_events:
            # Clean up duplicates
            df = pd.DataFrame(all_events).drop_duplicates(subset=['id'])
            df.to_csv("master.csv", index=False)
            print(f"Success! {len(df)} unique events saved to master.csv")
        else:
            print("No events found. Check if the website structure changed.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_premium_engine())
