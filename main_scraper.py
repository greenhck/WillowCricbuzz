import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

def parse_headers(url_part):
    headers = {}
    # Split by | or & to get individual components
    parts = re.split(r'[|&]', url_part)
    for part in parts:
        if '=' in part:
            # Key aur value ko split karke extra spaces saaf karein
            key_raw, val_raw = part.split('=', 1)
            key = key_raw.strip()
            value = urllib.parse.unquote(val_raw.strip())
            
            # Standard Header Names
            if key.lower() == 'user-agent': key = 'User-Agent'
            elif key.lower() == 'referer': key = 'Referer'
            elif key.lower() == 'origin': key = 'Origin'
            elif key.lower() == 'cookie': key = 'Cookie'
            elif key.lower() == 'drmscheme': key = 'drmScheme'
            elif key.lower() == 'drmlicense': key = 'drmLicense'
            
            headers[key] = value
    return headers

def get_tw_data():
    target_url = "https://t.me/s/HAPPYWARNING"
    try:
        response = requests.get(target_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        final_data = []
        
        messages = soup.find_all('div', class_='tgme_widget_message_bubble')

        for msg in messages:
            text_area = msg.find('div', class_='tgme_widget_message_text')
            if not text_area: continue

            # Text extraction with line breaks
            for br in text_area.find_all("br"): br.replace_with("\n")
            raw_content = text_area.get_text()
            lines = [l.strip() for l in raw_content.split('\n') if l.strip()]

            for i, line in enumerate(lines):
                if line.startswith('http'):
                    full_link = line
                    # Base link extract karein (sabse pehle pipe ya question mark tak)
                    base_url = re.split(r'[|?]', full_link)[0]
                    
                    # Name find karne ke liye pichli lines check karein
                    name = "LIVE STREAM"
                    for j in range(i-1, -1, -1):
                        if not lines[j].startswith('http'):
                            name = re.sub(r'[^\w\s\[\]\-]', '', lines[j]).strip()
                            if name: break
                    
                    # Headers/DRM extract karein
                    extracted_info = {}
                    if '|' in full_link:
                        info_part = full_link.split('|', 1)[1]
                        extracted_info = parse_headers(info_part)
                    elif '?' in full_link:
                        info_part = full_link.split('?', 1)[1]
                        extracted_info = parse_headers(info_part)

                    final_data.append({
                        "name": name.upper(),
                        "link": base_url,
                        "headers": extracted_info
                    })

        # Save to TW.json
        with open('TW.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_tw_data()
