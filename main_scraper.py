import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

def parse_headers(header_string):
    """
    Yeh function pipe (|) ke baad wale string ko split karke 
    saare headers (Referer, Origin, X-Forwarded-For, etc.) nikalta hai.
    """
    headers = {}
    # '&' aur '|' dono se split karein taaki nested headers mil sakein
    parts = re.split(r'[|&]', header_string)
    
    # Inhe hi allow karein taaki normal URL params headers me na ghusein
    valid_keys = [
        'user-agent', 'referer', 'origin', 'cookie', 
        'x-forwarded-for', 'drmscheme', 'drmlicense'
    ]

    for part in parts:
        if '=' in part:
            key_raw, val_raw = part.split('=', 1)
            key = key_raw.strip()
            value = urllib.parse.unquote(val_raw.strip())
            
            lkey = key.lower()
            if lkey in valid_keys:
                # Proper Case Formatting
                if lkey == 'user-agent': key = 'User-Agent'
                elif lkey == 'referer': key = 'Referer'
                elif lkey == 'origin': key = 'Origin'
                elif lkey == 'cookie': key = 'Cookie'
                elif lkey == 'x-forwarded-for': key = 'X-Forwarded-For'
                elif lkey == 'drmscheme': key = 'drmScheme'
                elif lkey == 'drmlicense': key = 'drmLicense'
                
                headers[key] = value
    return headers

def get_tw_data():
    target_url = "https://t.me/s/HAPPYWARNING"
    try:
        response = requests.get(target_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        final_data = []
        
        # Telegram messages scan karein
        messages = soup.find_all('div', class_='tgme_widget_message_bubble')

        for msg in messages:
            text_area = msg.find('div', class_='tgme_widget_message_text')
            if not text_area: continue

            # <br> ko newline me badlein taaki structure bana rahe
            for br in text_area.find_all("br"): br.replace_with("\n")
            raw_content = text_area.get_text()
            lines = [l.strip() for l in raw_content.split('\n') if l.strip()]

            for i, line in enumerate(lines):
                # Check if it's a link (normal or in <code>/<a> tags)
                if line.startswith('http'):
                    full_link = line
                    
                    # 1. Base URL aur Header Part alag karein
                    if '|' in full_link:
                        base_url, header_part = full_link.split('|', 1)
                        extracted_headers = parse_headers(header_part)
                    else:
                        base_url = full_link
                        extracted_headers = {}

                    # 2. Channel Name nikalne ka logic (peechli lines scan karein)
                    name = "LIVE STREAM"
                    for j in range(i-1, -1, -1):
                        if not lines[j].startswith('http'):
                            # Emojis aur special chars clean karein
                            name = re.sub(r'[^\w\s\[\]\-]', '', lines[j]).strip()
                            if name: break

                    # 3. List me add karein
                    final_data.append({
                        "name": name.upper(),
                        "link": base_url.strip(),
                        "headers": extracted_headers
                    })

        # Final JSON save karein
        with open('TW.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_tw_data()
