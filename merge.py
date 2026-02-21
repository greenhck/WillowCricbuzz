import os
import requests

def fetch_playlist():
    # all apis
    urls = os.getenv("ALLURL", "").strip().split('\n')
    combined_content = ["#EXTM3U\n"]
    
    # VLC User-Agent का उपयोग
    headers = {'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18'}

    for url in urls:
        url = url.strip()
        if not url: continue
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                lines = response.text.splitlines()
                for line in lines:
                    # Duplicate EXTM3U हटाना
                    if line.strip() and not line.startswith("#EXTM3U"):
                        combined_content.append(line)
            else:
                print(f"Error: {url} status {response.status_code}")
        except Exception as e:
            print(f"Skip {url}: {e}")

    # नए नाम से फ़ाइल सेव करना
    with open("pere-masala-perry-perry.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))

if __name__ == "__main__":
    fetch_playlist()
