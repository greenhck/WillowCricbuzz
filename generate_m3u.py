import os
import json
import requests

# Secret URL (GitHub Actions -> Secrets -> ALLJIO)
JSON_URL = os.getenv("ALLJIO")

if not JSON_URL:
    raise ValueError("ALLJIO secret is missing")

OUTPUT_FILE = "jiotv.m3u"


def fetch_json(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def generate_m3u(data):
    lines = ["#EXTM3U\n"]

    for ch in data:
        # Skip info / promo entries without stream
        mpd = ch.get("mpd")
        if not mpd:
            continue

        name = ch.get("name", "Unknown")
        logo = ch.get("logo", "")
        group = ch.get("category", "JioTV")
        referer = ch.get("referer", "")
        ua = ch.get("userAgent", "")
        token = ch.get("token", "")
        drm = ch.get("drm", {})

        # Build stream URL
        stream_url = mpd
        if token:
            stream_url = f"{mpd}?{token}"

        # IPTV entry
        lines.append(
            f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}'
        )

        # Optional headers
        if referer:
            lines.append(f'#EXTVLCOPT:http-referrer={referer}')
        if ua:
            lines.append(f'#EXTVLCOPT:http-user-agent={ua}')

        # DRM info as comments (players that support it will parse externally)
        if drm:
            for k, v in drm.items():
                lines.append(f"#KODIPROP:inputstream.adaptive.license_key={k}:{v}")

        lines.append(stream_url + "\n")

    return "\n".join(lines)


def main():
    data = fetch_json(JSON_URL)
    m3u_content = generate_m3u(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Saved {OUTPUT_FILE} with {len(data)} entries")


if __name__ == "__main__":
    main()
