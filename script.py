import requests
from datetime import datetime

url = "https://raw.githubusercontent.com/etcvai/ExtenderMax/refs/heads/main/iptv.m3u8"
response = requests.get(url).text
lines = response.splitlines()

def filter_and_save(group_name, file_name):
    output = ["#EXTM3U", f"# Updated: {datetime.now()}"]
    
    for i in range(len(lines)):
        # चेक करें कि क्या यह लाइन #EXTINF है और इसमें आपका group-title है
        if lines[i].startswith("#EXTINF") and f'group-title="{group_name}"' in lines[i]:
            output.append(lines[i]) # #EXTINF वाली लाइन
            
            # अगली लाइन्स (URL और OPTIONS) को तब तक जोड़ें जब तक अगला #EXTINF न आ जाए
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("#EXTINF"):
                    break
                if lines[j].strip(): # खाली लाइन न हो
                    output.append(lines[j])
                    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

# केवल वही ग्रुप निकालें जो आपको चाहिए
filter_and_save("ZEE5 IN", "zee5.m3u")
filter_and_save("SUN NXT", "sun_tv.m3u")
