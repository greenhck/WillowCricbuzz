import requests
import re
from datetime import datetime

url = "https://local.07live.workers.dev/playlist.m3u?user=999&pass=999"
headers = {"User-Agent": "OTT Navigator/1.7.1.2"}
new_logo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSjqPJebwHNucQ3X6qZdXE3oGi70_4wRH3SvQ&s"

# फाइल सुनिश्चित करें
open("tataplay.m3u", "a").close()

try:
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    lines = response.text.splitlines()

    output = ["#EXTM3U", f"# Updated: {datetime.now()}"]
    keyword = "🅴🆇🆃🆁🅰"

    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF") and keyword in lines[i]:
            # Regex का उपयोग करके tvg-logo की वैल्यू बदलें
            modified_line = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{new_logo}"', lines[i])
            output.append(modified_line)
            
            # अगली लाइन्स (URLs/Kodi Props) जोड़ें
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("#EXTINF"):
                    break
                if lines[j].strip():
                    output.append(lines[j])

    with open("tataplay.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print("Success: File updated with new logo.")

except Exception as e:
    print(f"Error: {e}")
