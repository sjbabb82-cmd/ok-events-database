import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

API_KEY = os.getenv("ANT_KEY")

def scrape():
    if not API_KEY:
        print("❌ ERROR: API Key 'ANT_KEY' not found!")
        return

    all_events = []
    
    # Let's do 50 pages (1,000 events)
    for page_num in range(1, 51): 
        print(f"Requesting Page {page_num}...")
        target_url = f"https://www.travelok.com/listings/search/15?page={page_num}"
        
        params = {
            "url": target_url,
            "x-api-key": API_KEY,
            "browser": "false" 
        }
        
        try:
            response = requests.get("https://api.scrapingant.com/v2/general", params=params, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # This is the 'Vision' part that looks for event cards
            items = soup.find_all(class_=["listing-item", "list-item"])
            
            if not items:
                print(f"⚠️ Page {page_num} appeared empty. Stopping.")
                break
                
            for item in items:
                title_el = item.find(['h3', 'h2', 'div'], class_=["listing-title", "title"])
                all_events.append({
                    "id": item.get('data-id', 'N/A'),
                    "title": title_el.text.strip() if title_el else "Unknown Event",
                    "url": "https://www.travelok.com" + item.find('a')['href'] if item.find('a') else "N/A"
                })
        except Exception as e:
            print(f"Error on page {page_num}: {e}")

    if all_events:
        new_df = pd.DataFrame(all_events)
        
        # --- FIXED SAFETY CHECK ---
        # Only compare if master.csv exists AND is not empty
        if os.path.exists("master.csv") and os.path.getsize("master.csv") > 0:
            try:
                old_df = pd.read_csv("master.csv")
                added = new_df[~new_df['id'].astype(str).isin(old_df['id'].astype(str))]
                added.to_csv("NEW_EVENTS.csv", index=False)
                print(f"✨ Found {len(added)} new events.")
            except Exception as e:
                print(f"Note: Could not read old master.csv ({e}). Skipping comparison.")
        
        # Save the new data as the new master
        new_df.to_csv("master.csv", index=False)
        print(f"✅ Success! Captured {len(all_events)} events into master.csv")
    else:
        print("⚠️ No events were found at all.")

if __name__ == "__main__":
    scrape()
