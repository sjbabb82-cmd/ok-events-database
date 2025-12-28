import requests
import pandas as pd

def direct_strike():
    # These headers are the "ID Card" that tells the site we are a real human
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    url = "https://www.travelok.com/listings/search/15"
    
    print(f"Attempting Direct Strike on {url}...")
    
    # We use a Session to handle any cookies they try to give us
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=15)
    
    # Calculate the size in KB
    size = len(response.content) / 1024
    print(f"RESPONSE SIZE: {size:.2f} KB")
    
    if size < 5:
        print("STILL BLOCKED: The response is too small to be the real site.")
        print("CONTENT PEEK:")
        print(response.text[:500])
    else:
        print("SUCCESS! We broke through the wall.")
        # Now we look for the IDs or JSON blobs hidden in the HTML
        if "listing" in response.text:
            print("Confirmed: Listing data found in the HTML source.")
        else:
            print("Wait... page loaded but 'listing' keyword is missing. Investigating structure...")

if __name__ == "__main__":
    direct_strike()
