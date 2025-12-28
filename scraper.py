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
            print(f"Shadow Piercing Scan Page {i}...")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(5) # Let Shadow DOM finish mounting
                
                # This script recursively searches every shadow root on the page for links
                extracted_data = await page.evaluate("""
                    () => {
                        const results = [];
                        const findLinks = (root) => {
                            if (!root) return;
                            
                            // Check standard links
                            root.querySelectorAll('a').forEach(link => {
                                const href = link.getAttribute('href');
                                if (href && href.includes('/view/')) {
                                    results.push({ url: href, text: link.innerText });
                                }
                            });
                            
                            // Pierce into Shadow DOMs
                            const elements = root.querySelectorAll('*');
                            elements.forEach(el => {
                                if (el.shadowRoot) {
                                    findLinks(el.shadowRoot);
                                }
                            });
                        };
                        
                        findLinks(document);
                        return results;
                    }
                """)

                page_count = 0
                for item in extracted_data:
                    href = item['url']
                    title = item['text']
                    
                    if href:
                        clean_url = "https://www.travelok.com" + href if href.startswith("/") else href
                        event_id = clean_url.split('/')[-1]
                        
                        all_events.append({
                            "id": event_id,
                            "title": title.strip() if title else "Event",
                            "url": clean_url
                        })
                        page_count += 1
                
                print(f"Page {i}: Captured {page_count} hidden links.")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:50]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['url'])
            # Filter out generic 'LEARN MORE' titles if better ones are available nearby
            df.to_csv("master.csv", index=False)
            print(f"Success: {len(df)} total unique events saved.")
        else:
            print("Shadow piercing failed. Site might be using canvas or encrypted data.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
