import requests
import json
from datetime import datetime

base_url = "http://89.187.191.54/stalker_portal/server/load.php"
mac = "00:1A:79:6E:FE:A7"
user_agent = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) Mag200 static Version/4.0.2 Safari/533.3"

headers = {"User-Agent": user_agent, "Cookie": f"mac={mac}"}

def get_token():
    try:
        resp = requests.get(base_url, params={"type": "stb", "action": "handshake"}, headers=headers, timeout=30)
        return resp.json().get('js', {}).get('token')
    except:
        return None

def get_playlist():
    token = get_token()
    if not token:
        print("Error: Handshake failed (Token not found)")
        return

    headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.get(base_url, params={"type": "itv", "action": "get_all_channels"}, headers=headers, timeout=30)
        data = resp.json().get('js', {}).get('data', [])
        
        if not data:
            print("No channels found in portal.")
            return

        output = ["#EXTM3U", f"# Updated: {datetime.now()}"]
        for ch in data:
            name = ch.get('name', 'Unknown')
            cmd = ch.get('cmd', '')
            # Link को क्लीन करना (ffrt हटाना)
            link = cmd.split(" ")[1] if " " in cmd else cmd
            
            output.append(f'#EXTINF:-1 tvg-id="{ch.get("id")}" tvg-logo="{ch.get("logo")}",{name}')
            output.append(link)

        with open("stalker.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print("Success: stalker.m3u created.")
    except Exception as e:
        print(f"Error fetching channels: {e}")

get_playlist()
