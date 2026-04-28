import requests
from datetime import datetime

# Portal Details
base_url = "http://89.187.191.54/stalker_portal/server/load.php"
mac = "00:1A:79:6E:FE:A7"
# सटीक MAG Device User-Agent
ua = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) Mag200 static Version/4.0.2 Safari/533.3"

headers = {
    "User-Agent": ua,
    "X-User-Agent": "Model: MAG250; SW: 2.20.0-r19-pub-250",
    "Cookie": f"mac={mac}",
    "Referer": "http://89.187.191.54/stalker_portal/c/",
    "Accept": "*/*",
    "Host": "89.187.191.54"
}

def get_token():
    params = {"type": "stb", "action": "handshake"}
    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=30)
        print(f"Handshake Status: {resp.status_code}")
        # अगर JSON नहीं है तो यहाँ एरर आएगा
        data = resp.json()
        return data.get('js', {}).get('token')
    except Exception as e:
        print(f"Handshake failed: {e}")
        return None

def get_playlist():
    token = get_token()
    if not token:
        return

    params = {
        "type": "itv",
        "action": "get_all_channels",
        "force_ch_link_check": "0",
        "jsvw": "1.1.0"
    }
    
    # टोकन को हेडर में जोड़ें
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=30)
        js_data = resp.json().get('js', {})
        data = js_data.get('data', [])
        
        if not data:
            print("No channels found in 'data' field.")
            return

        output = ["#EXTM3U", f"# Updated: {datetime.now()}"]
        for ch in data:
            name = ch.get('name', 'Unknown')
            cmd = ch.get('cmd', '')
            # ffrt/http लिंक क्लीन करें
            link = cmd.split(" ")[1] if " " in cmd else cmd
            
            output.append(f'#EXTINF:-1 tvg-id="{ch.get("id")}" tvg-logo="{ch.get("logo")}",{name}')
            output.append(link)

        with open("stalker.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print(f"Success! Saved {len(data)} channels to stalker.m3u")
        
    except Exception as e:
        print(f"Channel fetch failed: {e}")

get_playlist()
