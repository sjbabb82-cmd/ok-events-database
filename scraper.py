import asyncio
import os
from playwright.async_api import async_playwright

BROWSER_WS_ENDPOINT = os.getenv("BROWSER_WS_ENDPOINT")

async def investigate_small_payloads():
    async with async_playwright() as p:
        print("Connecting to browser for deep payload inspection...")
        browser = await p.chromium.connect_over_cdp(BROWSER_WS_ENDPOINT)
        page = await browser.new_page()

        async def handle_response(response):
            url = response.url
            # Filter for TravelOK and ignore the obvious junk (images/fonts/css)
            if "travelok.com" in url and not any(ext in url for ext in [".jpg", ".png", ".css", ".js", ".woff"]):
                try:
                    # Get the size and content type
                    size = len(await response.body()) / 1024 # KB
                    ctype = response.headers.get("content-type", "")
                    
                    print(f"CHECKING: {url[:60]}... | SIZE: {size:.1f}kb | TYPE: {ctype}")
                    
                    # If it's one of your ~13kb files, let's peek inside
                    if 10 <= size <= 20:
                        text = await response.text()
                        print(f"--- CONTENT PEEK (13kb range) ---")
                        print(text[:500]) # Show the first 500 characters
                        print(f"---------------------------------")
                        
                except Exception:
                    pass

        page.on("response", handle_response)

        print("Navigating to search page...")
        await page.goto("https://www.travelok.com/listings/search/15", wait_until="networkidle")
        await asyncio.sleep(8)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(investigate_small_payloads())
