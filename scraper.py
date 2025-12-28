import requests
import re
import pandas as pd

def clean_slate_extract():
    url = "https://www.travelok.com/listings/search/15"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    print("Fetching raw data...")
    r = requests.get(url, headers=headers)
    html = r.text
    
    # We are looking for the pattern: /view/NUMBER/SLUG
    # Example: /view/28491/redbud-festival
    pattern = r'/view/(\d+)/([a-z0-9\-]+)'
    matches = re.findall(pattern, html.lower())
    
    events = []
    for match in matches:
        listing_id = match[0]
        slug = match[1].replace('-', ' ').title()
        events.append({
            "id": listing_id,
            "title": slug,
            "url": f"https://www.travelok.com/listings/view/{listing_id}"
        })

    if events:
        df = pd.DataFrame(events).drop_duplicates(subset=['id'])
        df.to_csv("master.csv", index=False)
        print(f"SUCCESS: Captured {len(df)} events using pattern matching.")
        print(df.head(10))
    else:
        print("PATTERN MATCH FAILED.")
        # If this fails, we need to see exactly what follows the word 'listing'
        # Let's find the first instance of 'listing' and print the surrounding 200 chars
        idx = html.lower().find('listing')
        print(f"CONTEXT AROUND 'LISTING':\n...{html[idx:idx+300]}...")

if __name__ == "__main__":
    clean_slate_extract()
