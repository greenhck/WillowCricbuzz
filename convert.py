import requests
import json
import os

def generate_m3u():
    # gitlab json data
    json_url = os.getenv("BRHOT")
    if not json_url:
        print("Error: BRHOT json deleted/notfound")
        return

    try:
        response = requests.get(json_url)
        data = response.json()
        
        m3u_content = "#EXTM3U\n"
        
        for item in data:
            name = item.get("name", "Unknown")
            group = item.get("group", "General")
            logo = item.get("logo", "")
            
            # M3U Header line
            m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}\n'
            
            # Headers को KODI/IPTV फॉर्मेट में जोड़ना
            headers = item.get("headers", {})
            user_agent = item.get("user_agent", "")
            
            header_str = ""
            if user_agent:
                header_str += f"|User-Agent={user_agent}"
            if "Referer" in headers:
                header_str += f"&Referer={headers['Referer']}"
            if "Cookie" in headers:
                header_str += f"&Cookie={headers['Cookie']}"
            if "Origin" in headers:
                header_str += f"&Origin={headers['Origin']}"

            # DRM/License Check (For DASH)
            if item.get("type") == "dash":
                license_url = item.get("license_url", "")
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_type=widevine\n'
                m3u_content += f'#KODIPROP:inputstream.adaptive.license_key={license_url}\n'
                m3u_content += f'{item.get("mpd_url")}{header_str}\n'
            else:
                m3u_content += f'{item.get("m3u8_url")}{header_str}\n'

        with open("BRlatest.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print("BRlatest.m3u created successfully!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_m3u()
