import requests
import re

def raw_audit():
    url = "https://www.travelok.com/listings/search/15"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    r = requests.get(url, headers=headers)
    html = r.text
    
    print(f"--- HEAD CONTENT (First 1000 chars) ---\n{html[:1000]}")
    
    # Find all script tags that assign variables
    vars = re.findall(r'var\s+(\w+)\s*=', html)
    windows_vars = re.findall(r'window\.(\w+)\s*=', html)
    
    print(f"\n--- JS VARIABLES FOUND ---\n{list(set(vars + windows_vars))}")
    
    # Check if the text 'listing' appears anywhere, even if not in a link
    print(f"\n--- KEYWORD CHECK ---")
    print(f"Count of 'listing': {html.lower().count('listing')}")
    print(f"Count of 'event': {html.lower().count('event')}")

if __name__ == "__main__":
    raw_audit()
