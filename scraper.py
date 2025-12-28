import requests
import re

def final_diagnostic():
    url = "https://www.travelok.com/listings/search/15"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    r = requests.get(url, headers=headers)
    html = r.text
    
    print(f"--- DIAGNOSTIC REPORT ---")
    print(f"Total Chars: {len(html)}")
    
    # 1. Show the first 500 characters (Metadata/Framework check)
    print(f"START OF HTML:\n{html[:500]}\n")
    
    # 2. Show the last 2000 characters (This is where 'State' usually lives)
    print(f"END OF HTML:\n{html[-2000:]}\n")
    
    # 3. Find every <script> tag and report its size and first 50 chars
    scripts = re.findall(r'<script.*?>', html)
    print(f"Found {len(scripts)} script tags.")
    
    # 4. Search for the specific 'Listing' ID we know exists on the site
    # If this is 0, the data is definitely encoded/obfuscated.
    print(f"Literal 'listing' matches: {html.lower().count('listing')}")

if __name__ == "__main__":
    final_diagnostic()
