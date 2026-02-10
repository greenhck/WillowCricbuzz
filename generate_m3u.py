import os
import requests
import urllib.parse

JSON_URL = os.getenv("ALLJIO")
OUTPUT_FILE = "jiotv.m3u"

FIXED_UA = "plaYtv/7.1.5 (Linux;Android 13) ExoPlayerLib/2.11.6 YGX/69.69.69.69"
GROUP_TITLE = "Jiostar"

if not JSON_URL:
    raise ValueError("ALLJIO secret missing")


def fetch_json(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def generate_m3u(data):
    lines = ["#EXTM3U\n"]

    for ch in data:
        mpd = ch.get("mpd")
        if not mpd:
            continue

        name = ch.get("name", "Unknown")
        logo = ch.get("logo", "")
        tvg_id = ch.get("channel_id", "")
        token = ch.get("token", "")
        drm = ch.get("drm", {})

        cookie = token

        # URL with encoded |cookie=
        encoded_cookie = urllib.parse.quote(cookie, safe="")
        stream_url = f"{mpd}?%7Ccookie={encoded_cookie}"

        # EXTINF
        lines.append(
            f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="{GROUP_TITLE}" tvg-logo="{logo}",{name}'
        )

        # DRM
        if drm:
            lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
            for kid, key in drm.items():
                lines.append(
                    f"#KODIPROP:inputstream.adaptive.license_key={kid}:{key}"
                )

        # Fixed User-Agent
        lines.append(f"#EXTVLCOPT:http-user-agent={FIXED_UA}")

        # EXTHTTP cookie
        if cookie:
            lines.append(f'#EXTHTTP:{{"cookie":"{cookie}"}}')

        # Stream URL
        lines.append(stream_url + "\n")

    return "\n".join(lines)


def main():
    data = fetch_json(JSON_URL)
    m3u = generate_m3u(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

    print("✅ jiotv.m3u generated in RubyPlayer-compatible format")


if __name__ == "__main__":
    main()
