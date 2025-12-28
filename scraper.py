import asyncio
import os
import json
from playwright.async_api import async_playwright

BROWSER_WS_ENDPOINT = os.getenv("BROWSER_WS_ENDPOINT")

async def scan_network_for_api():
    async with async_playwright() as p:
        print("Launching Radio Scanner...")
        browser = await p.chromium.connect_over_cdp(BROWSER_WS_ENDPOINT)
        page = await browser.new_page()

        # We listen to every single 'conversation' the website has
        async def handle_response(response):
            url = response.url
            # We ignore Google/Ads/Trackers to find the actual data source
            if "travelok.com" in url and any(kw in url.lower() for kw in ["api", "listing", "search", "ajax"]):
                try:
                    # We check if the response is JSON (actual data)
                    ctype = response.headers.get("content-type", "")
                    if "json" in ctype:
                        print(f"\n[!] DATA STREAM DETECTED: {url}")
                        text = await response.text()
                        if "name" in text or "title" in text:
                            print(f"CONFIRMED: This stream contains event data.")
                            print(f"SAMPLE: {text[:200]}")
                except:
                    pass

        page.on("response", handle_response)

        print("Opening TravelOK and waiting for the background data to load...")
        # We go to the page and wait for it to be completely finished
        await page.goto("https://www.travelok.com/listings/search/15", wait_until="networkidle")
        
        # We wait an extra 10 seconds in case the data is 'lazy-loaded'
        await asyncio.sleep(10)
        
        await browser.close()
        print("\nScanner complete.")

if __name__ == "__main__":
    asyncio.run(scan_network_for_api())
