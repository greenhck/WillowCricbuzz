#!/usr/bin/env python3
"""
Fetch MovieBox API data and save to JSON files
This script runs on GitHub Actions to keep data fresh
"""

import httpx
import json
import os
import time
import hashlib
import hmac
import base64
from pathlib import Path

# Configuration
BASE_URL = "https://apig.inmoviebox.com/wefeed-mobile-bff"
SECRET_KEY_BASE64 = "76iRl07s0xSN9jqmEWAt79EBJZulIQIsV64FZr2O"
VERSION_HASH = "0d8421d946e2780cf9ebdd642640291d"

# Get from environment or use defaults
AUTH_TOKEN = os.getenv("MOVIEBOX_AUTH_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQyMjIwMjc3Mjg4MTc2Mzc0ODAsImV4cCI6MTc4NDAxMTE0MSwiaWF0IjoxNzc2MjM0ODQxfQ.PGSQgdAEaMDEYkavl4fQG7Afc0ITG_c93sYs061PmEE").strip()
DEVICE_ID = os.getenv("MOVIEBOX_DEVICE_ID", "06dbeab722cd1f28d06d1703317f377c").strip()

# Output directory (root of repository - files will be uploaded directly)
OUTPUT_DIR = Path(".")  # Current directory (root)


def generate_signature(method: str, path: str, timestamp: int) -> str:
    """Generate HMAC-MD5 signature for MovieBox API"""
    
    # Decode secret key
    secret_key = base64.b64decode(SECRET_KEY_BASE64)
    
    # Build string to sign
    string_to_sign = f"{method}\n\n\n0\n{timestamp}\n\n{path}"
    
    # Calculate HMAC-MD5
    signature_bytes = hmac.new(
        secret_key,
        string_to_sign.encode('utf-8'),
        hashlib.md5
    ).digest()
    
    # Encode to base64
    signature_base64 = base64.b64encode(signature_bytes).decode('utf-8')
    
    # Return in format: timestamp|2|signature
    return f"{timestamp}|2|{signature_base64}"


def fetch_homepage(tab_id: int = 2) -> dict:
    """Fetch homepage data from MovieBox API"""
    
    path = f"/wefeed-mobile-bff/tab-operating?tabId={tab_id}&version={VERSION_HASH}"
    url = f"{BASE_URL}/tab-operating?tabId={tab_id}&version={VERSION_HASH}"
    
    timestamp = int(time.time() * 1000)
    signature = generate_signature("GET", path, timestamp)
    
    client_info = {
        "package_name": "com.community.oneroom",
        "version_name": "3.0.13.0402.03",
        "version_code": 50020092,
        "os": "android",
        "os_version": "14",
        "install_ch": "google-play",
        "device_id": DEVICE_ID,
        "install_store": "gp",
        "gaid": "a8c31fc3-6da7-4be5-a9e8-0124c8746ed3",
        "brand": "motorola",
        "model": "moto g35 5G",
        "system_language": "en",
        "net": "NETWORK_4G",
        "region": "IN",
        "timezone": "Asia/Calcutta",
        "sp_code": "40470",
        "X-Play-Mode": "2",
        "X-Idle-Data": "1",
        "X-Family-Mode": "1",
        "X-Content-Mode": "0"
    }
    
    headers = {
        "x-play-mode": "2",
        "x-idle-data": "1",
        "x-family-mode": "1",
        "x-content-mode": "0",
        "x-client-info": json.dumps(client_info),
        "x-client-status": "0",
        "x-tr-signature": signature,
        "authorization": "Bearer " + AUTH_TOKEN,
        "user-agent": "com.community.oneroom/50020092 (Linux; U; Android 14; en_IN; moto g35 5G; Build/UOAS34.216-230-3; Cronet/146.0.7680.144)",
        "accept-encoding": "gzip, deflate, br"
    }
    
    print(f"Fetching homepage (tab {tab_id})...")
    print(f"URL: {url}")
    print(f"Signature: {signature}")
    
    try:
        response = httpx.get(url, headers=headers, timeout=30.0)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {len(data.get('data', {}).get('items', []))} items")
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def save_json(data: dict, filename: str):
    """Save data to JSON file"""
    if data is None:
        print(f"⚠️  Skipping {filename} - no data")
        return
    
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Saved to {filepath}")


def main():
    """Main function to fetch all data"""
    
    print("=" * 60)
    print("MovieBox API Data Fetcher")
    print("=" * 60)
    print()
    
    # Fetch different tabs
    tabs = {
        "homepage_trending.json": 2,      # Trending tab
        "homepage_movies.json": 3,        # Movies tab
        "homepage_anime.json": 4,         # Anime tab
        "homepage_kids.json": 5,          # Kids tab
        "homepage_education.json": 6,     # Education tab
    }
    
    for filename, tab_id in tabs.items():
        data = fetch_homepage(tab_id)
        save_json(data, filename)
        print()
        time.sleep(2)  # Rate limiting
    
    print("=" * 60)
    print("✅ All data fetched successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
