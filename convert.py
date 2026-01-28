import requests
import json
import os
import re

def extract_clearkey(license_url):
    # URL से keyid और key निकालने के लिए (Regex का उपयोग)
    keyid = re.search(r'keyid=([a-fA-F0-9]+)', license_url)
    key = re.search(r'key=([a-fA-F0-9]+)', license_url)
    
    if keyid and key:
        # ClearKey फॉर्मेट: keyid:key
        return f"{keyid.group(1)}:{key.group(1)}"
    return None

def generate_m3u():
    json_url = os.getenv("BRHOT")
    if not json_url:
        print("Error: BRHOT secret not found!")
        return

    try:
        response = requests.get(json_url)
        # अगर JSON के शुरू/आखिर में फालतू कोमा या ब्रैकेट हैं तो उसे साफ करें
        raw_data = response.text.strip()
        if raw_data.endswith(','): 
            raw_data = "[" + raw_data[:-1] + "]"
        
        data = json.loads(raw_data)
        
        m3u_content = "#EXTM3U\n"
        
        for item in data:
            name = item.get("name", "Unknown")
            group = item.get("group", "General")
            logo = item.get("logo", "")
            
            m3u_content += f'\n#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}\n'
            
            # Headers Setup
            headers = item.get("headers", {})
            user_agent = item.get("user_agent", "")
            header_str = f"|User-Agent={user_agent}"
            if "Cookie" in headers:
                header_str += f"&Cookie={headers['Cookie']}"
            if "Origin" in headers:
                header_str += f"&Origin={headers['Origin']}"
            if "Referer" in headers:
                header_str += f"&Referer={headers['Referer']}"

            # DASH + ClearKey Logic
            if item.get("type") == "dash":
                clearkey = extract_clearkey(item.get("license_url", ""))
                if clearkey:
                    m3u_content += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
                    m3u_content += f'#KODIPROP:inputstream.adaptive.license_key={clearkey}\n'
                
                m3u_content += f'{item.get("mpd_url")}{header_str}\n'
            
            # HLS Logic
            else:
                m3u_content += f'{item.get("m3u8_url")}{header_str}\n'

        with open("BRlatest.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print("Success: BRlatest.m3u with ClearKey updated!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_m3u()
