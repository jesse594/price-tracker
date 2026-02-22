"""Turn raw CSVs into ones with extra columns (averages, spread %, z-score, etc.)."""

import csv
import math
import os
from glob import glob

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("timestamp", "high", "low", "volume"):
            if k in r and r[k]:
                try:
                    r[k] = int(r[k]) if k in ("timestamp", "volume") else float(r[k])
                except ValueError:
                    r[k] = None
    return rows


def rolling_avg(vals, w):
    out = [None] * len(vals)
    for i in range(w - 1, len(vals)):
        chunk = [v for v in vals[i - w + 1 : i + 1] if v is not None]
        out[i] = sum(chunk) / len(chunk) if chunk else None
    return out


def rolling_std(vals, w):
    out = [None] * len(vals)
    for i in range(w - 1, len(vals)):
        chunk = [v for v in vals[i - w + 1 : i + 1] if v is not None]
        if len(chunk) < 2:
            continue
        m = sum(chunk) / len(chunk)
        var = sum((x - m) ** 2 for x in chunk) / len(chunk)
        out[i] = math.sqrt(var) if var > 0 else 0
    return out


def process(path):
    rows = [r for r in load_csv(path) if r.get("high") is not None and r.get("low") is not None]
    if not rows:
        return []
    highs = [r["high"] for r in rows]
    lows = [r["low"] for r in rows]
    mid = [(h + l) / 2 for h, l in zip(highs, lows)]
    spread = [h - l for h, l in zip(highs, lows)]
    spread_pct = [100 * (h - l) / ((h + l) / 2) if (h + l) > 0 else None for h, l in zip(highs, lows)]
    ma30 = rolling_avg(mid, 30)
    ma90 = rolling_avg(mid, 90)
    std30 = rolling_std(mid, 30)
    z = []
    for i in range(len(rows)):
        if ma30[i] is not None and std30[i] is not None and std30[i] > 0:
            z.append((mid[i] - ma30[i]) / std30[i])
        else:
            z.append(None)
    returns = [None] + [(mid[i] - mid[i - 1]) / mid[i - 1] if mid[i - 1] else None for i in range(1, len(mid))]
    vol = rolling_std(returns, 30)
    out = []
    for i, r in enumerate(rows):
        out.append({
            "timestamp": r.get("timestamp"),
            "high": r.get("high"),
            "low": r.get("low"),
            "volume": r.get("volume", 0),
            "mid_price": round(mid[i], 2),
            "spread": round(spread[i], 2),
            "spread_percent": round(spread_pct[i], 4) if spread_pct[i] is not None else None,
            "ma30": round(ma30[i], 2) if ma30[i] is not None else None,
            "ma90": round(ma90[i], 2) if ma90[i] is not None else None,
            "std30": round(std30[i], 4) if std30[i] is not None else None,
            "z_score": round(z[i], 4) if z[i] is not None else None,
            "rolling_volatility": round(vol[i], 6) if vol[i] is not None else None,
        })
    return out


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for path in sorted(glob(os.path.join(DATA_DIR, "*.csv"))):
        if "_processed" in path:
            continue
        base = os.path.splitext(os.path.basename(path))[0]
        print(f"Processing {base}...")
        try:
            out = process(path)
        except Exception as e:
            print(f"  Error: {e}")
            continue
        if not out:
            continue
        out_path = os.path.join(DATA_DIR, f"{base}_processed.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=out[0].keys())
            w.writeheader()
            w.writerows(out)
        print(f"  Wrote {len(out)} rows")
    print("Done.")


if __name__ == "__main__":
    main()
