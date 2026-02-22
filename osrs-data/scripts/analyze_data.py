"""Print simple stats for each processed CSV."""

import csv
import os
from glob import glob

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in r:
            if r[k] == "":
                r[k] = None
            else:
                try:
                    r[k] = int(r[k]) if k == "timestamp" else float(r[k])
                except ValueError:
                    pass
    return rows


def mean(x):
    return sum(x) / len(x) if x else 0


def analyze(path):
    base = os.path.basename(path).replace("_processed.csv", "").replace(".csv", "")
    name = base.replace("_", " ").title()
    rows = load(path)
    if not rows:
        print(f"{name}: no data\n")
        return
    spread = [r["spread_percent"] for r in rows if r.get("spread_percent") is not None]
    z = [r["z_score"] for r in rows if r.get("z_score") is not None]
    vol = [r["rolling_volatility"] for r in rows if r.get("rolling_volatility") is not None]
    n = len(z)
    above2 = sum(1 for v in z if v > 2) / n if n else 0
    below2 = sum(1 for v in z if v < -2) / n if n else 0
    ma30 = [r["ma30"] for r in rows if r.get("ma30") is not None]
    ma90 = [r["ma90"] for r in rows if r.get("ma90") is not None]
    crossovers = 0
    for i in range(1, min(len(ma30), len(ma90))):
        if ma30[i] is not None and ma90[i] is not None and ma30[i - 1] is not None and ma90[i - 1] is not None:
            if (ma30[i - 1] - ma90[i - 1]) * (ma30[i] - ma90[i]) < 0:
                crossovers += 1
    print(f"Item: {name}")
    print(f"  Avg spread %: {mean(spread):.2f}")
    print(f"  Avg z-score: {mean(z):.2f}")
    print(f"  Z > 2: {above2:.0%}  Z < -2: {below2:.0%}")
    if vol:
        print(f"  Volatility range: {min(vol):.4f} – {max(vol):.4f}")
    print(f"  MA30/MA90 crossovers: {crossovers}")
    print()


def main():
    files = sorted(glob(os.path.join(DATA_DIR, "*_processed.csv")))
    if not files:
        print("No processed files. Run process_data.py first.")
        return
    for path in files:
        try:
            analyze(path)
        except Exception as e:
            print(f"Error {path}: {e}\n")


if __name__ == "__main__":
    main()
