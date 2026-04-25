import requests
from datetime import datetime

url = "https://local.07live.workers.dev/playlist.m3u?user=999&pass=999"
headers = {"User-Agent": "OTT Navigator/1.7.1.2"}

try:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    lines = response.text.splitlines()

    output = ["#EXTM3U", f"# Updated: {datetime.now()}"]
    
    # कीवर्ड जिसे हम ढूँढ रहे हैं
    keyword = "🅴🆇🆃🆁🅰"

    for i in range(len(lines)):
        # चेक करें कि क्या लाइन #EXTINF है और उसमें कीवर्ड है
        if lines[i].startswith("#EXTINF") and keyword in lines[i]:
            output.append(lines[i]) # चैनल की जानकारी वाली लाइन
            
            # अगली लाइन्स (URLs/Kodi Props) को तब तक जोड़ें जब तक नया चैनल न आए
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("#EXTINF"):
                    break
                if lines[j].strip():
                    output.append(lines[j])

    # फाइल सेव करें
    with open("tataplay.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print(f"Success: Channels with '{keyword}' saved to tataplay.m3u")

except Exception as e:
    print(f"Error: {e}")
