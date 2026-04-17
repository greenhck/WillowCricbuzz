import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

def get_tw_data():
    # Telegram public channel link
    target_url = "https://t.me/s/HAPPYWARNING"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        final_data = []
        # Saare message bubbles find karein
        messages = soup.find_all('div', class_='tgme_widget_message_bubble')

        for msg in messages:
            text_area = msg.find('div', class_='tgme_widget_message_text')
            if not text_area:
                continue

            content = text_area.get_text(separator='|')
            lines = content.split('|')
            
            # URL aur Name extract karna
            for i, line in enumerate(lines):
                if 'http' in line:
                    raw_url = line.strip()
                    # Name dhundhne ke liye pichli lines check karein
                    name = "Unknown Stream"
                    if i > 0:
                        potential_name = lines[i-1].replace(':', '').strip()
                        if potential_name:
                            name = potential_name
                    
                    # URL Decoding for headers
                    decoded_url = urllib.parse.unquote(raw_url)

                    final_data.append({
                        "name": name.upper(),
                        "link": decoded_url
                    })

        # Save to TW.json
        with open('TW.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    get_tw_data()
