import os
import requests
import base64
import json

JSON_URL = os.getenv("ALLJIO")
OUTPUT_FILE = "jiotv.m3u"

if not JSON_URL:
    raise ValueError("ALLJIO secret is missing")


def hex_to_b64(hex_str):
    return base64.b64encode(bytes.fromhex(hex_str)).decode()


def fetch_json(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def generate_clearkey_license(drm):
    keys = []
    for kid, key in drm.items():
        keys.append({
            "kty": "oct",
            "kid": hex_to_b64(kid),
            "k": hex_to_b64(key)
        })

    lic = {
        "keys": keys,
        "type": "temporary"
    }

    lic_b64 = base64.b64encode(
        json.dumps(lic).encode()
    ).decode()

    return f"data:application/json;base64,{lic_b64}"


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

        # ✅ ClearKey for Android / ExoPlayer
        if drm:
            license_url = generate_clearkey_license(drm)
            lines.append("#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey")
            lines.append(f"#KODIPROP:inputstream.adaptive.license_key={license_url}")

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
