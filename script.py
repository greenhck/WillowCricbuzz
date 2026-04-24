import requests
from datetime import datetime

url = "https://raw.githubusercontent.com/etcvai/ExtenderMax/refs/heads/main/iptv.m3u8"
response = requests.get(url).text
lines = response.splitlines()

def filter_and_save(group_name, file_name):
    output = ["#EXTM3U", f"# Updated: {datetime.now()}"]
    
    for i in range(len(lines)):
        # Check for group-title match
        if lines[i].startswith("#EXTINF") and f'group-title="{group_name}"' in lines[i]:
            output.append(lines[i])
            
            # Extract following data until next #EXTINF
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("#EXTINF"):
                    break
                if lines[j].strip():
                    output.append(lines[j])
                    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

# Sabhi groups ki alag files
filter_and_save("ZEE5 IN", "zee5.m3u")
filter_and_save("SUN NXT", "sun_tv.m3u")
filter_and_save("JIO TV", "jiotv.m3u")
filter_and_save("SONY IN", "sony_set.m3u")
filter_and_save("SONAY EVENTS", "sony_events.m3u")
filter_and_save("myCo LIVE", "myco_live.m3u")
