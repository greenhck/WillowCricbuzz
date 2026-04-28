import requests
import json
from datetime import datetime

base_url = "http://89.187.191.54/stalker_portal/server/load.php"
mac = "00:1A:79:6E:FE:A7"
# OTT Navigator जैसा User-Agent इस्तेमाल करें
ua = "OTT Navigator/1.7.1.2 (Linux; Android 10; SM-G975F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36"

session = requests.Session()
session.headers.update({
    "User-Agent": ua,
    "X-User-Agent": "Model: MAG250; SW: 2.20.0-r19-pub-250",
    "Cookie": f"mac={mac}",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "http://89.187.191.54/stalker_portal/c/",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive"
})

def get_data():
    try:
        # 1. Handshake
        hs_resp = session.get(base_url, params={"type": "stb", "action": "handshake"}, timeout=30)
        
        # Debugging के लिए प्रिंट करें कि सर्वर क्या भेज रहा है
        if hs_resp.status_code != 200:
            print(f"HTTP Error: {hs_resp.status_code}")
            return

        try:
            token = hs_resp.json().get('js', {}).get('token')
        except:
            print("Server response is not JSON. It might be blocking GitHub.")
            print(f"Server content: {hs_resp.text[:200]}")
            return

        if not token:
            print("Token not found.")
            return
        
        # 2. Get Channels
        session.headers.update({"Authorization": f"Bearer {token}"})
        ch_params = {
            "type": "itv",
            "action": "get_all_channels",
            "jsvw": "1.1.0"
        }
        
        ch_resp = session.get(base_url, params=ch_params, timeout=30)
        
        # Check if the response is actually JSON
        try:
            data = ch_resp.json().get('js', {}).get('data', [])
        except:
            print("Channel list fetch failed. Server sent HTML instead of JSON.")
            return

        if not data:
            print("Portal returned empty channel list.")
            return

        # 3. Save File
        output = ["#EXTM3U", f"# Updated: {datetime.now()}"]
        for ch in data:
            name = ch.get('name', 'Unknown')
            cmd = ch.get('cmd', '')
            # Link formatting
            link = cmd.replace("ffrt ", "").split(" ")[0] if " " in cmd else cmd
            
            output.append(f'#EXTINF:-1 tvg-id="{ch.get("id")}" tvg-logo="{ch.get("logo")}",{name}')
            output.append(link)

        with open("stalker.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print(f"Success! {len(data)} channels saved.")

    except Exception as e:
        print(f"Script Error: {e}")

get_data()
