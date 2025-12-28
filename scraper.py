import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

API_KEY = os.getenv("ANT_KEY")

async def run_proprietary_engine():
    if not API_KEY:
        print("Error: ANT_KEY not found")
        return

    async with async_playwright() as p:
        # Use the proxy to bypass the data center block
        proxy_url = f"http://{API_KEY}:@proxy.scrapingant.com:8080"
        browser = await p.chromium.launch(proxy={"server": proxy_url})
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0"
        )
        page = await context.new_page()
        
        all_events = []
        
        for i in range(1, 6):
            url = f"https://www.travelok.com/listings/search/15?page={i}"
            print(f"Deep Scanning Page {i}...")
            
            try:
                # 1. Wait for Network to be completely quiet
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # 2. Force a human-like scroll and pause
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(5) 
                
                # 3. Capture a screenshot for the Action Artifacts
                if i == 1:
                    await page.screenshot(path="debug_screenshot.png")

                # 4. BROAD DISCOVERY: Find every link on the page
                # We look for ANY link containing '/view/' or text 'LEARN MORE'
                extracted = await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a'));
                        return links.map(l => ({
                            href: l.getAttribute('href'),
                            text: l.innerText,
                            parentText: l.parentElement?.innerText
                        })).filter(item => item.href && item.href.includes('/view/'));
                    }
                """)
                
                page_count = 0
                for item in extracted:
                    href = item['href']
                    # Use the URL to create an ID
                    event_id = href.split('/')[-1]
                    
                    # Try to find a real title: if text is 'LEARN MORE', use the parent text
                    raw_title = item['text']
                    if not raw_title or "LEARN MORE" in raw_title.upper():
                        # Pick the first few words of the parent text as a fallback
                        raw_title = item['parentText'].split('\\n')[0] if item['parentText'] else "Unknown Event"

                    all_events.append({
                        "id": event_id,
                        "title": raw_title.strip()[:100], # Clean and truncate
                        "url": f"https://www.travelok.com{href}" if href.startswith("/") else href
                    })
                    page_count += 1
                
                print(f"Page {i}: Found {page_count} events.")
                
            except Exception as e:
                print(f"Page {i} failed: {str(e)[:50]}")

        if all_events:
            df = pd.DataFrame(all_events).drop_duplicates(subset=['url'])
            df.to_csv("master.csv", index=False)
            print(f"Success! {len(df)} total events saved to master.csv")
        else:
            # If we STILL have zero, let's see the raw HTML structure
            html = await page.content()
            print(f"Structure Check: HTML length is {len(html)}. Top text: {html[:200]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_proprietary_engine())
