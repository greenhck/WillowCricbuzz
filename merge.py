import os
import requests
import re

def fetch_playlist():
    # Secret से URLs प्राप्त करें (प्रत्येक URL नई लाइन पर होना चाहिए)
    urls = os.getenv("ALLURL", "").strip().split('\n')
    combined_content = ["#EXTM3U\n"]
    
    # VLC User-Agent ताकि डेटा सही मिले
    headers = {
        'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18'
    }

    for url in urls:
        url = url.strip()
        if not url: continue
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                lines = response.text.splitlines()
                for line in lines:
                    # फालतू EXTM3U टैग्स और खाली लाइन्स को हटाना
                    if line.strip() and not line.startswith("#EXTM3U"):
                        combined_content.append(line)
                combined_content.append("\n") # गैप के लिए
            else:
                print(f"Failed: {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines("\n".join(combined_content))

if __name__ == "__main__":
    fetch_playlist()
