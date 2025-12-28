import requests
import re

def audit_structure():
    url = "https://www.travelok.com/listings/search/15"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("Retrieving shell...")
    response = requests.get(url, headers=headers, timeout=30)
    html = response.text

    print(f"Total HTML Length: {len(html)} characters")

    # 1. Check for the most common data scripts
    containers = ["__NEXT_DATA__", "__PRELOADED_STATE__", "window._listingData", "window.data"]
    for c in containers:
        if c in html:
            print(f"DETECTED CONTAINER: {c}")
        else:
            print(f"NOT FOUND: {c}")

    # 2. Look for any script tag that is unusually large (likely where the data is)
    scripts = re.findall(r'<script.*?> (.*?) </script>', html, re.DOTALL | re.VERBOSE)
    print(f"Found {len(scripts)} script tags.")
    
    for i, s in enumerate(scripts):
        if len(s) > 1000:
            print(f"Script #{i} is large ({len(s)} chars). Start of content: {s[:100].strip()}")

    # 3. Look for the 'Listing ID' pattern again with a wider net
    # Maybe they use 'id=' or 'data-id='
    ids = re.findall(r'id=["\'](\d+)["\']', html)
    print(f"Found {len(ids)} numeric IDs in the HTML.")

if __name__ == "__main__":
    audit_structure()
