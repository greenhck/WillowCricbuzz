import requests
import re

url = "https://raw.githubusercontent.com/etcvai/ExtenderMax/refs/heads/main/iptv.m3u8"
response = requests.get(url).text

def save_group(group_name, file_name):
    pattern = r'(#EXTINF.*group-title="' + group_name + r'".*?)(?=#EXTINF|$)'
    matches = re.findall(pattern, response, re.DOTALL)
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "".join(matches))

# Files बनाएँ
save_group("ZEE5 IN", "zee5.m3u")
save_group("SUN NXT", "sun_tv.m3u")
