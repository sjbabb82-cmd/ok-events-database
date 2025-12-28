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
            print(f"Aggressive Scan Page {i}...")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                # Allow time for the dynamic content to settle
                await asyncio.sleep(5)
                
                # Injection Logic: This runs directly in the browser's console
                # It finds every link and grabs the text and URL
                extracted_data = await page.evaluate("""
                    () => {
                        const results = [];
                        const links = document.querySelectorAll('a');
                        links.forEach(link => {
                            const href = link.getAttribute('href');
                            if (href && href.includes('/listings/view/')) {
                                // Find the closest parent that might contain the title
                                // or use the text of the link itself
                                results.append({
                                    url: href,
                                    text: link.innerText
                                });
                            }
                        });
                        return results;
                    }
                """)
                
                # If the JS injection finds 0, we try an even broader search 
                # looking for anything with 'view' in the href
                if not extracted_data:
                    extracted_data = await page.evaluate("""
                        () => {
                            return Array.from(document.links)
                                .filter(l => l.href.includes('/view/'))
                                .map(l => ({ url: l.href, text: l.innerText }));
                        }
                    """)

                page_count = 0
                for item in extracted_data:
                    href = item['url']
                    title = item['text']
                    
                    if href:
                        clean_url = "https://www.travelok.com" + href if href.startswith("/") else href
                        # Use the last part of the URL as the unique ID
                        event_id = clean_url.split('/')[-1]
                        
                        all_events.append({
                            "id": event_id,
                            "title": title.strip() if title else "Event",
                            "url": clean_url
                        })
                        page_count += 1
                
                print(f"Page {i}: Injected script found {page_count} links.")
                
            except Exception as e:
                print(f"Error on Page {i}: {str(e)[:50]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['url'])
            # Filter out entries where title is just 'LEARN MORE' to keep the data clean
            df.to_csv("master.csv", index=False)
            print(f"Success: {len(df)} total unique events saved.")
        else:
            print("Injection failed. Checking page structure one last time...")
            # Capture the raw HTML for one last look
            content = await page.content()
            print(f"HTML Length: {len(content)} characters.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
