import os
import json
import time
import requests
from datetime import datetime, timedelta, timezone
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

API_KEY    = os.getenv("FINNHUB_API_KEY")
GCS_BUCKET = os.getenv("GCS_BUCKET_NAME")

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "NVDA", "META",
    "JPM",  "BAC",  "GS",    "V",    "MA",
    "JNJ",  "PFE",  "UNH",   "ABBV", "MRK",
    "XOM",  "CVX",  "COP",   "WMT",  "AMZN"
]

def get_last_trading_day():
    today = datetime.now(timezone.utc).date()
    day = today - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day

def fetch_quote(symbol, date):
    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if data.get("c", 0) == 0:
        print(f"  No data for {symbol}")
        return None
    return {
        "symbol":      symbol,
        "date":        str(date),
        "open":        data.get("o"),
        "high":        data.get("h"),
        "low":         data.get("l"),
        "close":       data.get("c"),
        "prev_close":  data.get("pc"),
        "change":      data.get("d"),
        "change_pct":  data.get("dp"),
        "volume":      None,
        "ingested_at": datetime.now(timezone.utc).isoformat()
    }

def upload_to_gcs(records, date):
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    file_path = f"raw/candles/{date}.json"
    blob = bucket.blob(file_path)
    content = "\n".join(json.dumps(r) for r in records)
    blob.upload_from_string(content, content_type="application/json")
    print(f"\nUploaded {len(records)} records to gs://{GCS_BUCKET}/{file_path}")

def main():
    date = get_last_trading_day()
    print(f"Fetching quotes for: {date}\n")
    records = []
    for i, symbol in enumerate(TICKERS):
        print(f"  [{i+1}/20] {symbol}...")
        record = fetch_quote(symbol, date)
        if record:
            records.append(record)
        time.sleep(1)
    if not records:
        print("No records fetched. Check your API key.")
        return
    upload_to_gcs(records, date)
    print("Done!")

if __name__ == "__main__":
    main()
