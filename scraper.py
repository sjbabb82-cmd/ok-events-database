import requests
import json
import pandas as pd
import re

def run_extraction():
    url = "https://www.travelok.com/listings/search/15"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.google.com/"
    }

    print(f"Connecting to {url}...")
    response = requests.get(url, headers=headers, timeout=30)
    
    # Save the full HTML for a one-time "Structure Audit"
    with open("source.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("Analyzing 128KB payload...")

    # Strategy A: Look for JSON blobs inside <script> tags
    # This regex looks for common data containers in modern web apps
    data_match = re.search(r'id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
    
    events = []

    if data_match:
        print("Found __NEXT_DATA__ blob. Parsing...")
        full_json = json.loads(data_match.group(1))
        # This path varies, so we'll look for anything that looks like a listing
        # We search the dictionary recursively for the 'listings' key
        def find_listings(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == 'listings' and isinstance(v, list):
                        return v
                    res = find_listings(v)
                    if res: return res
            elif isinstance(obj, list):
                for item in obj:
                    res = find_listings(item)
                    if res: return res
            return None
        
        events = find_listings(full_json) or []

    # Strategy B: Fallback to raw ID scraping if JSON parsing fails
    if not events:
        print("JSON blob empty. Attempting raw ID extraction...")
        # Find everything that looks like /view/NUMBER/Name
        raw_links = re.findall(r'/listings/view/(\d+)/([^"\'>\s]+)', response.text)
        for link in raw_links:
            events.append({"id": link[0], "slug": link[1]})

    if events:
        df = pd.DataFrame(events).drop_duplicates()
        df.to_csv("master.csv", index=False)
        print(f"SUCCESS: Extracted {len(df)} events.")
        print(f"Sample: {df.iloc[0].to_dict() if not df.empty else 'N/A'}")
    else:
        print("FAILED: Page loaded but data is invisible to current extraction logic.")
        print("Check 'source.html' in the artifacts to see where the data is hidden.")

if __name__ == "__main__":
    run_extraction()
