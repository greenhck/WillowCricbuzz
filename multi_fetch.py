import requests
import os
import re

def fetch_content(url):
    try:
        # User-Agent बदलकर डेटा फेच करना ताकि ब्लॉक न हो
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=15)
        return r.text if r.status_code == 200 else ""
    except:
        return ""

def process_source(content, source_type):
    lines = content.split('\n')
    output = ""
    
    if source_type == "BRSPORTS1": # Sony Sports logic
        # यहाँ हम हर #EXTINF के बाद वाली URL लाइन को पकड़ते हैं
        matches = re.findall(r'(#EXTINF:.*?,.*?)\n(https?://[^\s#]+)', content)
        for info, url in matches:
            info = re.sub(r'group-title=".*?"', 'group-title="Sony Sports"', info)
            output += f"{info}\n{url}\n"

    elif source_type == "BRSPORTS2": # Hotstar logic (Filter Others/Sports)
        # Hotstar में ClearKey और Headers साथ में होते हैं
        chunks = re.split(r'(?=#EXTINF)', content)
        for chunk in chunks:
            if 'group-title="Others"' in chunk or 'group-title="Sports"' in chunk:
                chunk = re.sub(r'group-title=".*?"', 'group-title="Hotstar Sports"', chunk)
                output += chunk.strip() + "\n"

    elif source_type == "BRSPORTS3": # Fancode logic
        matches = re.findall(r'(#EXTINF:.*?,.*?)\n(https?://[^\s#]+)', content)
        for info, url in matches:
            info = re.sub(r'group-title=".*?"', 'group-title="Fancode"', info)
            output += f"{info}\n{url}\n"

    elif source_type == "BRSPORTS4": # WPL logic
        chunks = re.split(r'(?=#EXTINF)', content)
        for chunk in chunks:
            if 'group-title="WPL |Live"' in chunk:
                chunk = re.sub(r'group-title=".*?"', 'group-title="WPL"', chunk)
                output += chunk.strip() + "\n"

    return output

def main():
    final_m3u = "#EXTM3U\n"
    
    # (BRSPORTS1, BRSPORTS2, etc.)
    sources = [
        ("BRSPORTS1", "BRSPORTS1"),
        ("BRSPORTS2", "BRSPORTS2"),
        ("BRSPORTS3", "BRSPORTS3"),
        ("BRSPORTS4", "BRSPORTS4"),
        # भविष्य में यहाँ ("BRSPORTS5", "TYPE") जोड़ें
    ]

    for secret_name, s_type in sources:
        url = os.getenv(secret_name)
        if url:
            raw_content = fetch_content(url)
            if raw_content:
                final_m3u += process_source(raw_content, s_type)

    filename = "telegramgroup-chatstadium-ke-maalik-ne-banaya-hai-blackrootAP-pass-is-in99.m3u"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_m3u)

if __name__ == "__main__":
    main()
