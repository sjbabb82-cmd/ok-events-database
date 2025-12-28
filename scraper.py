import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_travel_ok():
    url = "https://www.travelok.com/listings/search/15"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    print("Fetching listings...")
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    events = []
    
    # TravelOK listings are typically wrapped in 'listing' or 'result' classes
    # We are going to find every link that points to a 'view' page
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        if '/listings/view/' in href:
            # Extract the ID and the Title/Name from the URL and link text
            # URL format: /listings/view/12345/event-name
            parts = href.split('/')
            if len(parts) >= 4:
                listing_id = parts[3]
                title = link.get_text(strip=True) or parts[-1].replace('-', ' ').title()
                
                events.append({
                    "id": listing_id,
                    "title": title,
                    "url": f"https://www.travelok.com{href}"
                })

    if events:
        df = pd.DataFrame(events).drop_duplicates(subset=['id'])
        df.to_csv("master.csv", index=False)
        print(f"SUCCESS: Extracted {len(df)} unique events.")
        print(df.head())
    else:
        print("FAILED: No listings found in the HTML structure. Dumping names of all classes found...")
        # Emergency backup: print all class names found in the page
        classes = set([cls for tag in soup.find_all(True) if tag.get('class') for cls in tag.get('class')])
        print(f"Available CSS classes: {list(classes)[:20]}")

if __name__ == "__main__":
    scrape_travel_ok()
