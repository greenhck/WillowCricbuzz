import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

def get_tw_data():
    target_url = "https://t.me/s/HAPPYWARNING"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        final_data = []
        
        # Har message bubble ko alag process karein
        messages = soup.find_all('div', class_='tgme_widget_message_bubble')

        for msg in messages:
            text_area = msg.find('div', class_='tgme_widget_message_text')
            if not text_area:
                continue

            # Step 1: Text ko clean karein aur links ko identify karein
            # Hum <br>, <blockquote>, <pre> sabko handle karenge
            for br in text_area.find_all("br"):
                br.replace_with("\n")
            
            raw_text = text_area.get_text()
            lines = [l.strip() for l in raw_text.split('\n') if l.strip()]

            for i, line in enumerate(lines):
                # Agar line ek URL hai
                if line.startswith('http'):
                    full_link = line
                    # Agar link ke andar pipes (|) hain, unhe properly decode karein
                    decoded_link = urllib.parse.unquote(full_link)
                    
                    # Name nikalne ke liye pichli line dekhein jo link na ho
                    name = "LIVE STREAM"
                    for j in range(i-1, -1, -1):
                        if not lines[j].startswith('http'):
                            # Emojis aur faltu symbols saaf karein
                            clean_name = re.sub(r'[^\w\s\[\]]', '', lines[j]).strip()
                            if clean_name:
                                name = clean_name
                                break
                    
                    # Duplicate check: Agar link pehle se list mein hai to skip karein
                    if not any(d['link'] == decoded_link for d in final_data):
                        final_data.append({
                            "name": name.upper(),
                            "link": decoded_link
                        })

        # Save to TW.json
        with open('TW.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_tw_data()
