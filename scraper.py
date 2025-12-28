import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import urllib.parse

# This looks for the secret you named 'ANT_KEY' in GitHub Settings
API_KEY = os.getenv("ANT_KEY")

def scrape():
    # Debug print: This lets you check the logs to see if the key loaded
    # (It only shows the first 4 characters for security)
    if API_KEY:
        print(f"✅ API Key loaded successfully (Starts with: {API_KEY[:4]}...)")
    else:
        print("❌ ERROR: API Key 'ANT_KEY' not found in Environment Variables!")
        return

    all_events = []
    
    # Range (1, 51) gets you 50 pages (approx 1,000 events)
    for page_num in range(1, 51): 
        print(f"Requesting Page {page_num}...")
        
        target_url = f"https://www.travelok.com/listings/search/15?page={page_num}"
        # We encode the URL so the proxy understands it correctly
        encoded_url = urllib.parse.quote_plus(target_url)
        
        # We use 'browser=false' to save credits since we just need the HTML
        proxy_url = f"https://api.scrapingant.com/v2/general?url={encoded_url}&x-api-key={API_KEY}&browser=false"
        
        try:
            response = requests.get(proxy_url, timeout=30)
            if response.status_code != 200:
                print(f"⚠️ Proxy returned error {response.status_code}. Stopping.")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all('div', class_='listing-item')
            
            if not items:
                print(f"Reached the end or got blocked at page {page_num}.")
                break
                
            for item in items:
                title_el = item.find('div', class_='listing-title')
                all_events.append({
                    "id": item.get('data-id'),
                    "title": title_el.text.strip() if title_el else "N/A",
                    "date": item.find('div', class_='listing-date').text.strip() if item.find('div', class_='listing-date') else "N/A",
                    "img": item.find('img')['src'] if item.find('img') else "N/A"
                })
        except Exception as e:
            print(f"Error on page {page_num}: {e}")

    if all_events:
        new_df = pd.DataFrame(all_events)
        
        # Compare with last run
        if os.path.exists("master.csv"):
            old_df = pd.read_csv("master.csv")
            # Items in NEW but not in OLD
            added = new_df[~new_df['id'].astype(str).isin(old_df['id'].astype(str))]
            # Items in OLD but not in NEW
            removed = old_df[~old_df['id'].astype(str).isin(new_df['id'].astype(str))]
            
            added.to_csv("NEW_EVENTS.csv", index=False)
            removed.to_csv("DELETED_EVENTS.csv", index=False)
            print(f"✨ Found {len(added)} new and {len(removed)} deleted events.")
        
        new_df.to_csv("master.csv", index=False)
        print(f"✅ Master file updated with {len(all_events)} records.")
    else:
        print("⚠️ No events were found. Check the TravelOK website structure.")

if __name__ == "__main__":
    scrape()
