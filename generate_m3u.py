import os
import requests
import urllib.parse

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

        ua = ch.get("userAgent", "")
        referer = ch.get("referer", "")
        origin = referer
        token = ch.get("token", "")
        drm = ch.get("drm", {})

        # token is cookie
        cookie = token

        # Build headers for RubyPlayer (URL | format)
        headers = {}

        if ua:
            headers["User-Agent"] = ua
        if cookie:
            headers["Cookie"] = cookie
        if referer:
            headers["Referer"] = referer
        if origin:
            headers["Origin"] = origin

        header_str = "&".join(
            f"{k}={urllib.parse.quote(v, safe='~=%:/;,+')}"
            for k, v in headers.items()
        )

        stream_url = mpd
        if header_str:
            stream_url = f"{mpd}|{header_str}"

        # EXTINF
        lines.append(
            f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}'
        )

        # DRM (RubyPlayer reads this correctly)
        if drm:
            lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
            for kid, key in drm.items():
                lines.append(
                    f"#KODIPROP:inputstream.adaptive.license_key={kid}:{key}"
                )

        # URL last
        lines.append(stream_url + "\n")

    return "\n".join(lines)


def main():
    data = fetch_json(JSON_URL)
    m3u = generate_m3u(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

    print("✅ jiotv.m3u generated (RubyPlayer format)")


if __name__ == "__main__":
    main()
