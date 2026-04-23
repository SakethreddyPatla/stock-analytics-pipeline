from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

DBT_CMD = (
    'dbt {command} '
    '--project-dir /opt/airflow/dbt_project '
    '--profiles-dir /opt/airflow/dbt_project '
    '--log-path /tmp/dbt-logs '
    '--target-path /tmp/dbt-target'
)

with DAG(
    dag_id='stock_pipeline',
    description='Daily stock data pipeline: Finnhub -> GCS -> BigQuery -> dbt',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='0 6 * * 1-5',
    catchup=False,
    tags=['stocks', 'finnhub', 'bigquery', 'dbt'],
) as dag:

    fetch_quotes = BashOperator(
        task_id='fetch_quotes',
        bash_command='python /opt/airflow/ingestion/fetch_daily_candles.py',
    )

    load_to_bq = BashOperator(
        task_id='load_to_bigquery',
        bash_command='python /opt/airflow/ingestion/load_to_bigquery.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=DBT_CMD.format(command='run'),
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=DBT_CMD.format(command='test'),
    )

    dbt_docs_generate = BashOperator(
        task_id='dbt_docs_generate',
        bash_command=DBT_CMD.format(command='docs generate'),
    )

    upload_docs = BashOperator(
        task_id='upload_docs_to_gcs',
        bash_command=(
            'gsutil -m cp '
            '/tmp/dbt-target/catalog.json '
            '/tmp/dbt-target/manifest.json '
            '/tmp/dbt-target/index.html '
            'gs://$GCS_BUCKET_NAME/dbt-docs/'
        ),
    )

    fetch_quotes >> load_to_bq >> dbt_run >> dbt_test >> dbt_docs_generate >> upload_docs
