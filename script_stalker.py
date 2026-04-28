import requests
import json
from datetime import datetime

# Stalker Portal Details
base_url = "http://89.187.191.54/stalker_portal/server/load.php"
mac = "00:1A:79:6E:FE:A7"
user_agent = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) Mag200 static Version/4.0.2 Safari/533.3"

headers = {"User-Agent": user_agent, "Cookie": f"mac={mac}"}

def get_token():
    params = {"type": "stb", "action": "handshake"}
    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=20)
        return resp.json()['js']['token']
    except:
        return None

def get_playlist():
    token = get_token()
    if not token:
        print("Token failed!")
        return

    headers["Authorization"] = f"Bearer {token}"
    params = {"type": "itv", "action": "get_all_channels"}
    
    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=20)
        data = resp.json()['js']['data']
        
        output = ["#EXTM3U", f"# Updated: {datetime.now()}"]
        
        for ch in data:
            name = ch.get('name', 'Unknown')
            # Stalker links ko play karne ke liye format
            cmd = ch.get('cmd', '')
            if cmd.startswith("ffrt "): 
                link = cmd.split(" ")[1]
            else:
                link = cmd
                
            output.append(f'#EXTINF:-1 tvg-id="{ch.get("id")}" tvg-logo="{ch.get("logo")}",{name}')
            output.append(link)

        with open("stalker.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print("stalker.m3u created!")
    except Exception as e:
        print(f"Error: {e}")

get_playlist()
