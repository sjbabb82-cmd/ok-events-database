import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

BROWSER_WS_ENDPOINT = os.getenv("BROWSER_WS_ENDPOINT")

async def run_premium_engine():
    if not BROWSER_WS_ENDPOINT:
        print("Error: BROWSER_WS_ENDPOINT not found. Check GitHub Secrets.")
        return

    async with async_playwright() as p:
        print("Connecting to Browserless.io...")
        try:
            browser = await p.chromium.connect_over_cdp(BROWSER_WS_ENDPOINT)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()
            
            all_events = []
            
            for i in range(1, 6):
                url = f"https://www.travelok.com/listings/search/15?page={i}"
                print(f"Deep Scanning Page {i}...")
                
                # 1. Navigate with a long timeout
                await page.goto(url, wait_until="networkidle", timeout=90000)
                
                # 2. Wait 10 seconds for the "React/Vue Hydration" (the data to pop in)
                await asyncio.sleep(10)
                
                # 3. Scroll to trigger any lazy-loading content
                await page.mouse.wheel(0, 2000)
                await asyncio.sleep(2)

                # 4. BROAD LINK DISCOVERY: Find every link matching the event pattern
                extracted = await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href*="/view/"]'));
                        return links.map(l => {
                            // Find the closest text-heavy parent to grab date/location info
                            const container = l.closest('div[class*="card"], .listing-item') || l.parentElement;
                            return {
                                href: l.getAttribute('href'),
                                text: l.innerText,
                                context: container ? container.innerText : ""
                            };
                        });
                    }
                """)

                if not extracted and i == 1:
                    print("Warning: Page 1 returned 0 results. Saving debug_site.html...")
                    html_content = await page.content()
                    with open("debug_site.html", "w", encoding="utf-8") as f:
                        f.write(html_content)

                for item in extracted:
                    href = item['href']
                    event_id = href.split('/')[-1]
                    
                    # Clean up the text
                    title = item['text'].split('\\n')[0].strip()
                    if len(title) < 3 or title.upper() == "LEARN MORE":
                        title = item['context'].split('\\n')[0].strip()

                    all_events.append({
                        "id": event_id,
                        "title": title[:100],
                        "url": f"https://www.travelok.com{href}" if href.startswith("/") else href,
                        "raw_info": item['context'].replace('\\n', ' | ')[:200]
                    })
                
                print(f"Page {i}: Found {len(extracted)} potential event links.")

            if all_events:
                df = pd.DataFrame(all_events).drop_duplicates(subset=['id'])
                df.to_csv("master.csv", index=False)
                print(f"Success! {len(df)} total events saved to master.csv")
            else:
                print("Final Check: 0 events found across all pages.")

        except Exception as e:
            print(f"Critical Engine Failure: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_premium_engine())
