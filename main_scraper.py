import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

def parse_headers(header_string):
    headers = {}
    # '&' aur '|' par split karein
    parts = re.split(r'[|&]', header_string)
    
    valid_keys = [
        'user-agent', 'referer', 'origin', 'cookie', 
        'x-forwarded-for', 'drmscheme', 'drmlicense'
    ]

    for part in parts:
        if '=' in part:
            key_raw, val_raw = part.split('=', 1)
            key = key_raw.strip()
            # Double decoding for nested values
            value = urllib.parse.unquote(urllib.parse.unquote(val_raw.strip()))
            
            lkey = key.lower()
            if lkey in valid_keys:
                mapping = {
                    'user-agent': 'User-Agent',
                    'referer': 'Referer',
                    'origin': 'Origin',
                    'cookie': 'Cookie',
                    'x-forwarded-for': 'X-Forwarded-For',
                    'drmscheme': 'drmScheme',
                    'drmlicense': 'drmLicense'
                }
                headers[mapping[lkey]] = value
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

            for br in text_area.find_all("br"): br.replace_with("\n")
            lines = [l.strip() for l in text_area.get_text().split('\n') if l.strip()]

            for i, line in enumerate(lines):
                if line.startswith('http'):
                    # CRITICAL: Pehle poore link ko decode karein (%7C ko | banane ke liye)
                    full_link = urllib.parse.unquote(line)
                    
                    if '|' in full_link:
                        base_url, header_part = full_link.split('|', 1)
                        extracted_headers = parse_headers(header_part)
                    else:
                        base_url = full_link
                        extracted_headers = {}

                    # Name logic
                    name = "LIVE STREAM"
                    for j in range(i-1, -1, -1):
                        if not lines[j].startswith('http'):
                            name = re.sub(r'[^\w\s\[\]\-]', '', lines[j]).strip()
                            if name: break

                    final_data.append({
                        "name": name.upper(),
                        "link": base_url.strip(),
                        "headers": extracted_headers
                    })

        with open('TW.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_tw_data()
