import os
import requests

# GitHub Secret: ALLJIO (JSON URL)
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

        # 🔑 token IS cookie
        cookies = token

        # Stream URL (token optional but kept)
        stream_url = mpd
        if token:
            stream_url = f"{mpd}?{token}"

        # EXTINF
        lines.append(
            f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}'
        )

        # Headers
        if referer:
            lines.append(f"#EXTVLCOPT:http-referrer={referer}")
        if ua:
            lines.append(f"#EXTVLCOPT:http-user-agent={ua}")

        # 🍪 Cookies
        if cookies:
            lines.append(f"#EXTVLCOPT:http-cookie={cookies}")
            lines.append(
                f"#KODIPROP:inputstream.adaptive.http_headers=Cookie={cookies}"
            )

        # 🔐 DRM (ClearKey)
        if drm:
            lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
            for kid, key in drm.items():
                lines.append(
                    f"#KODIPROP:inputstream.adaptive.license_key={kid}:{key}"
                )

        # Stream URL
        lines.append(stream_url + "\n")

    return "\n".join(lines)


def main():
    data = fetch_json(JSON_URL)
    m3u = generate_m3u(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

    print("✅ jiotv.m3u generated successfully")


if __name__ == "__main__":
    main()
