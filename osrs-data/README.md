# OSRS GE data pipeline

Fetch GE price history from the Wiki, add some stats (spread, averages, z-score), then print a quick summary per item.

**Run:**

1. `pip install -r requirements.txt`  (optional)
2. `python scripts/fetch_data.py`     → saves CSVs in `data/`
3. `python scripts/process_data.py`  → adds columns, saves `*_processed.csv`
4. `python scripts/analyze_data.py`  → prints stats

**More items:** Edit `ITEM_IDS` in `scripts/fetch_data.py`, then run 2–4 again.

**SSL errors on fetch:** Fix your Python certs (e.g. macOS: run the certificate installer that came with Python).
