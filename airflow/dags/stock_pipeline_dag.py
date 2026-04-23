from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

with DAG(
    dag_id='stock_pipeline',
    description='Daily stock data pipeline: Finnhub -> GCS -> BigQuery -> dbt',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='0 6 * * 1-5',
    catchup=False,
    tags=['stocks', 'finnhub', 'bigquery', 'dbt'],
) as dag:
    # Task 1: Pull data from Finnhub and land in GCS
    fetch_quotes = BashOperator(
        task_id='fetch_quotes',
        bash_command='python /opt/airflow/ingestion/fetch_daily_candles.py',
    )

    # Task 2: Load from GCS into BigQuery raw layer
    load_to_bq = BashOperator(
        task_id='load_to_bigquery',
        bash_command='python /opt/airflow/ingestion/load_to_bigquery.py',
    )

    # Task 3: Run dbt models (staging → marts)
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    # Task 4: Run dbt tests — fail the DAG if data quality breaks
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )
    # Task 5: Generate dbt docs (catalog.json + manifest.json)
    dbt_docs_generate = BashOperator(
        task_id='dbt_docs_generate',
        bash_command='dbt docs generate --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    # Task 6: Copy generated docs to a GCS bucket so they are publicly accessible
    upload_docs = BashOperator(
        task_id='upload_docs_to_gcs',
        bash_command=(
            'gsutil -m cp -r '
            '/opt/airflow/dbt_project/target/catalog.json '
            '/opt/airflow/dbt_project/target/manifest.json '
            '/opt/airflow/dbt_project/target/index.html '
            'gs://${GCS_BUCKET_NAME}/dbt-docs/'
        ),
    )

    # Define the pipeline order
    fetch_quotes >> load_to_bq >> dbt_run >> dbt_test