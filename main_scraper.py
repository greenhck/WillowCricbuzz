import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

def parse_headers(url_part):
    headers = {}
    # Headers ko '&' aur '|' se split karke clean karein
    parts = re.split(r'[|&]', url_part)
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            # Standard header format (User-agent -> User-Agent)
            if key.lower() == 'user-agent': key = 'User-Agent'
            elif key.lower() == 'referer': key = 'Referer'
            elif key.lower() == 'origin': key = 'Origin'
            elif key.lower() == 'cookie': key = 'Cookie'
            
            headers[key] = urllib.parse.unquote(value)
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

            # Get clean lines
            for br in text_area.find_all("br"): br.replace_with("\n")
            lines = [l.strip() for l in text_area.get_text().split('\n') if l.strip()]

            for i, line in enumerate(lines):
                if line.startswith('http'):
                    raw_link = line
                    base_url = raw_link.split('|')[0].split('?')[0]
                    
                    # Name find karein
                    name = "LIVE STREAM"
                    for j in range(i-1, -1, -1):
                        if not lines[j].startswith('http'):
                            name = re.sub(r'[^\w\s\[\]]', '', lines[j]).strip()
                            break
                    
                    # Headers extract karein
                    extracted_headers = {}
                    if '|' in raw_link:
                        header_part = raw_link.split('|', 1)[1]
                        extracted_headers = parse_headers(header_part)
                    elif '?' in raw_link:
                        query_part = raw_link.split('?', 1)[1]
                        extracted_headers = parse_headers(query_part)

                    final_data.append({
                        "name": name.upper(),
                        "link": base_url,
                        "headers": extracted_headers
                    })

        with open('TW.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_tw_data()
    
