import os
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCS_BUCKET = os.getenv("GCS_BUCKET_NAME")

def get_last_trading_day():
    today = datetime.now(timezone.utc).date()
    day = today-timedelta(days=1)
    while day.weekday() >=5:
        day -= timedelta(days=1)
    return day

def load_to_bigquery(date):
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.raw.stock_quotes"
    gcs_uri = f"gs://{GCS_BUCKET}/raw/candles/{date}.json"

    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        ignore_unknown_values=True,
    )
    print(f"Loading {gcs_uri} -> {table_id}")
    load_job = client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
    load_job.result()

    table = client.get_table(table_id)
    print(f"Done, Table now has {table.num_rows} total rows")

def main():
    date = get_last_trading_day()
    load_to_bigquery(date)

if __name__ == "__main__":
    main()