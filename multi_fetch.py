import requests
import os
import re

def fetch_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=20)
        return r.text if r.status_code == 200 else ""
    except:
        return ""

def process_source(content, source_type):
    output = ""
    
    if source_type == "BRSPORTS1": # Sony Sports
        matches = re.findall(r'(#EXTINF:.*?,.*?)\n?(https?://[^\s#]+)', content)
        for info, url in matches:
            info = re.sub(r'group-title=".*?"', 'group-title="Sony Sports"', info)
            output += f"{info}\n{url}\n"

    elif source_type == "BRSPORTS2": # Hotstar (Others/Sports only)
        chunks = re.split(r'(?=#EXTINF)', content)
        for chunk in chunks:
            if 'group-title="Others"' in chunk or 'group-title="Sports"' in chunk:
                chunk = re.sub(r'group-title=".*?"', 'group-title="Hotstar Sports"', chunk)
                output += chunk.strip() + "\n"

    elif source_type == "BRSPORTS3": # Fancode
        matches = re.findall(r'(#EXTINF:.*?,.*?)\n?(https?://[^\s#]+)', content)
        for info, url in matches:
            info = re.sub(r'group-title=".*?"', 'group-title="Fancode"', info)
            output += f"{info}\n{url}\n"

    elif source_type == "BRSPORTS4": # WPL
        chunks = re.split(r'(?=#EXTINF)', content)
        for chunk in chunks:
            if 'group-title="WPL |Live"' in chunk:
                chunk = re.sub(r'group-title=".*?"', 'group-title="WPL"', chunk)
                output += chunk.strip() + "\n"

    elif source_type == "BRSPORTS5": # Prime Sports (DASH ClearKey)
        # इसमें हम पूरे ब्लॉक को उठाएंगे जिसमें #KODIPROP शामिल है
        chunks = re.split(r'(?=#EXTINF)', content)
        for chunk in chunks:
            if 'group-title="Prime sports"' in chunk:
                output += chunk.strip() + "\n"

    elif source_type == "BRSPORTS6": # Fox Sports Filter
        # यहाँ हम Fox Sports 501, 502 आदि को ढूंढ रहे हैं
        matches = re.findall(r'(#EXTINF:.*?,.*?Fox Sports.*?)\s+(https?://[^\s#|]+)', content)
        for info, url in matches:
            # ग्रुप को बदलकर Fox Sports करना
            info = re.sub(r'group-title=".*?"', 'group-title="Fox Sports"', info)
            output += f"{info}\n{url}\n"

    return output

def main():
    final_m3u = "#EXTM3U\n"
    
    # यहाँ 6 तक के सोर्स लिंक हैं
    sources = [
        ("BRSPORTS1", "BRSPORTS1"),
        ("BRSPORTS2", "BRSPORTS2"),
        ("BRSPORTS3", "BRSPORTS3"),
        ("BRSPORTS4", "BRSPORTS4"),
        ("BRSPORTS5", "BRSPORTS5"),
        ("BRSPORTS6", "BRSPORTS6"),
    ]

    for secret_name, s_type in sources:
        url = os.getenv(secret_name)
        if url:
            print(f"Fetching {secret_name}...")
            raw_content = fetch_content(url)
            if raw_content:
                final_m3u += process_source(raw_content, s_type)

    filename = "telegramgroup-chatstadium-ke-maalik-ne-banaya-hai-blackrootAP-pass-is-in99.m3u"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_m3u)
    print("Done! File Saved.")

if __name__ == "__main__":
    main()
