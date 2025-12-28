import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# This looks for the secret you named 'ANT_KEY' in GitHub Settings
API_KEY = os.getenv("ANT_KEY")

def scrape():
    if API_KEY:
        print(f"✅ API Key loaded successfully (Starts with: {API_KEY[:4]}...)")
    else:
        print("❌ ERROR: API Key 'ANT_KEY' not found in Environment Variables!")
        return

    all_events = []
    
    for page_num in range(1, 51): 
        print(f"Requesting Page {page_num}...")
        
        target_url = f"https://www.travelok.com/listings/search/15?page={page_num}"
        
        # ScrapingAnt parameters
        proxy_url = "https://api.scrapingant.com/v2/general"
        params = {
            "url": target_url,
            "x-api-key": API_KEY,
            "browser": "false"  # Saves credits; TravelOK's initial HTML contains the data
        }
        
        try:
            response = requests.get(proxy_url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"⚠️ Proxy returned error {response.status_code}. Content: {response.text[:100]}")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for the event cards
            items = soup.find_all('div', class_='listing-item')
            
            if not items:
                print(f"Reached the end or got blocked at page {page_num}.")
                # Debug: print a bit of the HTML to see what's actually there
                break
                
            for item in items:
                title_el = item.find('div', class_='listing-title')
                date_el = item.find('div', class_='listing-date')
                img_el = item.find('img')
                link_el = item.find('a')
                
                all_events.append({
                    "id": item.get('data-id'),
                    "title": title_el.text.strip() if title_el else "N/A",
                    "date": date_el.text.strip() if date_el else "N/A",
                    "img": img_el['src'] if img_el else "N/A",
                    "url": "https://www.travelok.com" + link_el['href'] if link_el else "N/A"
                })
        except Exception as e:
            print(f"Error on page {page_num}: {e}")

    if all_events:
        new_df = pd.DataFrame(all_events)
        
        if os.path.exists("master.csv"):
            old_df = pd.read_csv("master.csv")
            added = new_df[~new_df['id'].astype(str).isin(old_df['id'].astype(str))]
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
