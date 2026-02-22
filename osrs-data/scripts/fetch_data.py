"""Grab price history from the Wiki API and save as CSV per item."""

import csv
import json
import os
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Add more (id, "filename_slug") to get more items
ITEM_IDS = [
    (2, "steel_cannonball"),
    (453, "coal"),
    (314, "feather"),
    (565, "blood_rune"),
    (21902, "dragon_crossbow"),
]

BASE_URL = "https://prices.runescape.wiki/api/v1/osrs/timeseries"
HEADERS = {"User-Agent": "OSRS-GE-Data/1.0"}
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def fetch_one(item_id, step="5m"):
    url = f"{BASE_URL}?id={item_id}&timestep={step}"
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        out = json.loads(resp.read().decode())
    data = out.get("data") or out
    if not isinstance(data, list):
        return []
    rows = []
    for p in data:
        if not isinstance(p, dict):
            continue
        ts = p.get("timestamp")
        high = p.get("avgHighPrice") or p.get("high")
        low = p.get("avgLowPrice") or p.get("low")
        vol = (p.get("highPriceVolume") or 0) + (p.get("lowPriceVolume") or 0)
        if ts is not None:
            rows.append({"timestamp": ts, "high": high, "low": low, "volume": vol})
    return rows


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for item_id, slug in ITEM_IDS:
        print(f"Fetching {slug}...")
        try:
            rows = fetch_one(item_id)
        except Exception as e:
            print(f"  Failed: {e}")
            continue
        if not rows:
            print("  No data.")
            continue
        path = os.path.join(DATA_DIR, f"{slug}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "high", "low", "volume"])
            w.writeheader()
            w.writerows(rows)
        print(f"  Saved {len(rows)} rows")
        time.sleep(0.5)
    print("Done.")


if __name__ == "__main__":
    main()
