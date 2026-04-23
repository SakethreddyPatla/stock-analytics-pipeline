FROM apache/airflow:2.9.0

USER root
RUN apt-get update && apt-get install -y git curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y google-cloud-cli && \
    apt-get clean

USER airflow
RUN pip install --no-cache-dir \
    dbt-bigquery==1.7.0 \
    google-cloud-storage \
    google-cloud-bigquery \
    requests \
    python-dotenv
