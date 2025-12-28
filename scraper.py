import requests
import pandas as pd
import sys

def direct_strike():
    # High-quality headers to mimic a real visitor
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive"
    }

    url = "https://www.travelok.com/listings/search/15"
    
    print(f"Attempting Direct Strike on {url}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        size = len(response.content) / 1024
        print(f"RESPONSE SIZE: {size:.2f} KB")
        print(f"HTTP STATUS: {response.status_code}")

        if size < 5:
            print("--- BLOCK DETECTED ---")
            print("The response is too small. Here is the '0.5kb' content:")
            print(response.text[:1000]) # Print more of the block page to identify the firewall
        else:
            print("--- BREAKTHROUGH ---")
            if "listing" in response.text.lower():
                print("Data found in HTML. Proceeding to extraction...")
                # Simple extraction test
                count = response.text.lower().count("/listings/view/")
                print(f"Approximate events found: {count}")
            else:
                print("HTML loaded but no events found. Structure check needed.")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    direct_strike()
