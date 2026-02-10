import os
import requests

JSON_URL = os.getenv("ALLJIO")
OUTPUT_FILE = "jiotv.m3u"

if not JSON_URL:
    raise ValueError("ALLJIO secret is missing")


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
        group = ch.get("category", "JioTV")
        referer = ch.get("referer", "")
        ua = ch.get("userAgent", "")
        token = ch.get("token", "")
        drm = ch.get("drm", {})

        stream_url = mpd + (f"?{token}" if token else "")

        lines.append(
            f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}'
        )

        if referer:
            lines.append(f"#EXTVLCOPT:http-referrer={referer}")
        if ua:
            lines.append(f"#EXTVLCOPT:http-user-agent={ua}")

        # 🔐 ONLY CHANGE: scheme = clearkey
        if drm:
            lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
            for kid, key in drm.items():
                lines.append(
                    f"#KODIPROP:inputstream.adaptive.license_key={kid}:{key}"
                )

        lines.append(stream_url + "\n")

    return "\n".join(lines)


def main():
    data = fetch_json(JSON_URL)
    m3u = generate_m3u(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

    print("jiotv.m3u generated successfully")


if __name__ == "__main__":
    main()
