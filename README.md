# Stock Analytics Pipeline

> An end-to-end Analytics Engineering portfolio project — from raw API data to production-ready dashboards with full CI/CD automation.

![CI](https://github.com/SakethreddyPatla/stock-analytics-pipeline/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/SakethreddyPatla/stock-analytics-pipeline/actions/workflows/cd.yml/badge.svg)

---

## The Problem This Project Solves

Most analytics teams face the same pain points:

- **Data scattered across sources** with no single source of truth
- **Manual reporting** — someone downloads a CSV every morning and pastes it into Excel
- **No data quality checks** — broken pipelines go unnoticed until a stakeholder complains
- **No version control for SQL** — transformations live in someone's laptop
- **No CI/CD** — untested code goes straight to production

This project solves all of these by building a **production-grade, fully automated data pipeline** for stock market data — the kind of system a professional Analytics Engineer would build at a real company.

Instead of manual work, every day at 6am the pipeline:
1. Automatically pulls fresh stock data from an API
2. Lands it in cloud storage as a raw immutable record
3. Loads it into BigQuery
4. Transforms it through tested dbt models
5. Makes it available to Power BI dashboards
6. Validates data quality — and fails loudly if something breaks

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│                    Finnhub REST API                             │
│           (20 stocks across 4 sectors, daily OHLCV)            │
└─────────────────────────────┬───────────────────────────────────┘
                              │ Python ingestion script
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                              │
│              Google Cloud Storage (GCS)                         │
│         raw/candles/YYYY-MM-DD.json  ← newline-delimited JSON  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ BigQuery Load Job
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WAREHOUSE LAYER                            │
│                        BigQuery                                 │
│   ┌──────────┐    ┌──────────────┐    ┌───────────────────┐   │
│   │   raw    │ →  │   staging    │ →  │      marts        │   │
│   │          │    │              │    │                   │   │
│   │stock_    │    │stg_stock_    │    │dim_company        │   │
│   │quotes    │    │quotes        │    │fct_daily_trading  │   │
│   │          │    │              │    │mart_sector_perf   │   │
│   └──────────┘    └──────────────┘    └───────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ dbt Core
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TRANSFORMATION LAYER                          │
│                       dbt Core                                  │
│   • Staging models    → clean and type raw data                 │
│   • Mart models       → business-ready aggregates               │
│   • Macros            → reusable Jinja logic                    │
│   • Tests             → 13 data quality checks                  │
│   • Docs              → auto-generated data catalog             │
└─────────────────────────────┬───────────────────────────────────┘
                              │ Apache Airflow DAG
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                            │
│                    Apache Airflow                               │
│   fetch_quotes → load_to_bq → dbt_run → dbt_test →            │
│   dbt_docs_generate → upload_docs_to_gcs                       │
│                  Runs Mon-Fri at 6am UTC                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │ DirectQuery / Import
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVING LAYER                                │
│                       Power BI                                  │
│   • Daily Market Overview dashboard                             │
│   • KPI cards, bar charts, scatter plots                        │
│   • Sector performance analysis                                 │
│   • Interactive slicers by date and sector                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      CI/CD LAYER                                │
│                   GitHub Actions                                │
│   On PR:     sqlfluff lint → dbt parse  (blocks bad merges)    │
│   On merge:  sqlfluff lint → dbt parse → deploy simulation     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Data Source | Finnhub REST API | Free tier, 60 calls/min, real market data |
| Ingestion | Python + requests | Lightweight, full control over the pipeline |
| Raw Storage | Google Cloud Storage | Immutable landing zone, decoupled from BQ |
| Warehouse | BigQuery | Serverless, scalable, integrates with dbt + Power BI |
| Transformation | dbt Core | Version-controlled SQL, testing, documentation |
| Orchestration | Apache Airflow (Docker) | Industry standard, DAG-based scheduling |
| Dashboarding | Power BI | Direct BigQuery connector, rich visuals |
| CI/CD | GitHub Actions | Free, integrates with repo, automates quality checks |
| SQL Linting | sqlfluff | Enforces consistent SQL style across the team |

---

## Project Structure

```
stock-analytics-pipeline/
├── ingestion/
│   ├── fetch_daily_candles.py      # Pulls quotes from Finnhub API → GCS
│   └── load_to_bigquery.py         # Idempotent GCS → BigQuery loader
│
├── dbt_project/
│   └── stock_analytics/
│       ├── models/
│       │   ├── staging/
│       │   │   ├── sources.yml         # Raw BigQuery source definition
│       │   │   ├── stg_stock_quotes.sql # Clean + type raw data
│       │   │   └── stg_stock_quotes.yml # Column tests
│       │   └── marts/
│       │       ├── dim_company.sql      # Company dimension (sector, industry)
│       │       ├── fct_daily_trading.sql # Daily trading fact table
│       │       ├── mart_sector_performance.sql # Sector aggregates
│       │       └── schema.yml           # Mart tests
│       ├── macros/
│       │   ├── pct_to_label.sql        # % change → human label (strong up/down)
│       │   ├── is_market_open.sql          # Date utility macro
│       │   └── generate_schema_name.sql # Clean BigQuery dataset routing
│       ├── seeds/
│       │   └── tickers.csv             # 20 stocks × sector/industry metadata
│       └── .sqlfluff                   # SQL linting rules
│
├── airflow/
│   ├── dags/
│   │   └── stock_pipeline_dag.py   # Full pipeline DAG
│   ├── Dockerfile                  # Custom Airflow image with dbt + gcloud
│   └── docker-compose.yml          # Local Airflow stack
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  # PR checks: lint + parse
│       └── cd.yml                  # Merge checks: lint + parse + deploy
│
├── docs/
│   └── stock_analytics_dashboard.pbix  # Power BI dashboard
│
├── requirements.txt
└── README.md
```

---

## Data Model

### Staging Layer
**`stg_stock_quotes`** — cleaned and typed raw quotes
- Casts all prices to `NUMERIC`
- Adds `day_direction` (up/down/flat)
- Filters nulls and invalid symbols

### Marts Layer

**`dim_company`** — company dimension table (loaded from seed)
```
symbol | company_name | sector | industry | sector_category
```

**`fct_daily_trading`** — one row per stock per trading day
```
symbol | trade_date | sector | close_price | price_change_pct |
performance_label | intraday_range | intraday_range_pct
```

**`mart_sector_performance`** — daily sector aggregates
```
trade_date | sector | avg_change_pct | stocks_up | stocks_down |
sector_sentiment | top_performer | worst_performer
```

### dbt Macros
- **`pct_to_label`** — converts a `%` column into `strong up / up / flat / down / strong down`
- **`is_weekend`** — returns true if a date falls on Saturday or Sunday
- **`generate_schema_name`** — overrides dbt's default dataset naming to produce clean names (`marts` not `staging_marts`)

### Data Tests (13 total)
| Test | Model | Column |
|---|---|---|
| not_null | stg_stock_quotes | symbol, trade_date |
| accepted_values | stg_stock_quotes | symbol (20 tickers), day_direction |
| not_null | dim_company | symbol, sector |
| unique | dim_company | symbol |
| accepted_values | dim_company | sector |
| not_null | fct_daily_trading | symbol, trade_date |
| accepted_values | fct_daily_trading | performance_label |
| not_null | mart_sector_performance | trade_date, sector |
| accepted_values | mart_sector_performance | sector_sentiment |

---

## Problems Faced & How We Solved Them

### 1. Finnhub `/stock/candle` endpoint returned 403
**Problem:** The free tier of Finnhub doesn't support the OHLCV candle endpoint — it requires a paid plan.

**Solution:** Switched to the `/quote` endpoint which is fully free and returns open, high, low, close, prev_close, change, and change_pct. Slightly different schema but richer for analytics (prev_close and change_pct are more useful than raw volume).

---

### 2. GCP service account key creation blocked by org policy
**Problem:** The organisation policy `iam.disableServiceAccountKeyCreation` prevented downloading a JSON credentials file — a common corporate security control.

**Solution:** Used **Application Default Credentials (ADC)** via `gcloud auth application-default login` instead. This is actually the more secure, recommended approach — credentials are stored locally by gcloud and picked up automatically by all Google Cloud libraries without any file to accidentally commit to git.

---

### 3. BigQuery datasets named `staging_staging` and `staging_marts`
**Problem:** dbt-BigQuery by default prepends the profile's `dataset` value to any custom schema, producing ugly names like `staging_marts` instead of `marts`.

**Solution:** Created a custom `generate_schema_name` macro that overrides dbt's default behaviour — if a model defines a custom schema, use that name exactly without prepending anything.

```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.dataset }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

---

### 4. Duplicate rows from multiple DAG runs
**Problem:** Running the Airflow DAG multiple times during testing loaded the same date's data multiple times into `raw.stock_quotes`, causing duplicate rows in all downstream models.

**Solution:** Implemented an **idempotent load pattern** — before loading data for a date, delete any existing rows for that date first:

```python
# Delete existing rows for this date
client.query(f"DELETE FROM `{table_id}` WHERE date = '{date}'").result()
# Then load fresh data
client.load_table_from_uri(gcs_uri, table_id, job_config=job_config).result()
```

No matter how many times the pipeline runs for the same date, the result is always exactly 20 rows — one per ticker.

---

### 5. Airflow Docker container couldn't write dbt logs
**Problem:** dbt tried to write logs to `/opt/airflow/dbt_project/logs/` which is a Windows-mounted volume. The Docker container (Linux user `airflow`) didn't have write permission to Windows NTFS folders.

**Solution:** Redirected dbt's log and target paths to `/tmp` inside the container using `--log-path` and `--target-path` flags — `/tmp` is always writable inside Linux containers.

```python
'dbt run --project-dir /opt/airflow/dbt_project '
'--log-path /tmp/dbt-logs '
'--target-path /tmp/dbt-target'
```

---

### 6. GitHub Actions CI/CD YAML files corrupted by PowerShell encoding
**Problem:** PowerShell's `Set-Content` saves files with UTF-8 BOM (Byte Order Mark) by default. GitHub Actions YAML parser rejects BOM-encoded files with `MissingSectionHeaderError`. Additionally, string replacement operations on the files introduced corrupted special characters (e.g. `ÃƒÂ¢` instead of `—`).

**Solution:** Used `[System.IO.File]::WriteAllText()` with explicit `UTF8Encoding($false)` to write without BOM. For files that got too corrupted, created them directly in the **GitHub web editor** which always saves as clean UTF-8.

---

### 7. sqlfluff couldn't lint dbt models in CI (no BigQuery connection)
**Problem:** The `dbt` templater for sqlfluff requires an actual BigQuery connection to compile Jinja templates before linting. CI environments don't have credentials.

**Solution:** Switched to the `jinja` templater in `.sqlfluff` with `apply_dbt_builtins = true`. This resolves `{{ ref() }}`, `{{ source() }}` and `{{ config() }}` without connecting to the database. For custom macros like `{{ pct_to_label() }}`, added a `-- noqa: TMP,PRS` comment to suppress the undefined variable warning on that specific line.

---

### 8. `dbt compile` failed in CI without credentials
**Problem:** Even with a dummy `profiles.yml`, `dbt compile` tries to introspect the database to verify source tables exist — which fails without real credentials.

**Solution:** Switched to `dbt parse` which performs the same DAG validation (resolves all `ref()`, `source()`, macro calls, checks for circular dependencies) without making any database connection. `dbt parse` is the correct tool for credential-free CI validation.

---

### 9. Package version conflicts in CI
**Problem:** Installing `dbt-bigquery==1.7.0` with the latest `google-cloud-bigquery` caused `AttributeError: module 'google.cloud.bigquery._helpers' has no attribute '_CELLDATA_FROM_JSON'` — an internal API that was removed in a newer version.

**Solution:** Pinned all Google Cloud package versions explicitly in both workflow files:
```
dbt-bigquery==1.7.0
google-cloud-bigquery==3.11.4
google-cloud-storage==2.10.0
```

This is a general best practice — always pin dependencies in CI to ensure reproducible builds.

---

## How to Run Locally

### Prerequisites
- Python 3.11+
- Docker Desktop
- Google Cloud SDK (`gcloud`)
- Power BI Desktop (Windows)
- Finnhub account (free) → [finnhub.io](https://finnhub.io)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/stock-analytics-pipeline.git
cd stock-analytics-pipeline

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Authenticate with GCP
gcloud auth application-default login

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your values:
# FINNHUB_API_KEY=your_key
# GCP_PROJECT_ID=your_project_id
# GCS_BUCKET_NAME=your_bucket_name
```

### Run the pipeline manually

```bash
# Fetch today's stock data and land in GCS
python ingestion/fetch_daily_candles.py

# Load GCS → BigQuery raw layer
python ingestion/load_to_bigquery.py

# Run dbt transformations
cd dbt_project/stock_analytics
dbt run
dbt test

# Generate dbt docs
dbt docs generate
dbt docs serve  # opens http://localhost:8080
```

### Run with Airflow (Docker)

```bash
cd airflow
docker compose up -d

# Open http://localhost:8084
# Login: admin / admin
# Trigger the stock_pipeline DAG manually
```

---

## CI/CD Pipeline

### On every Pull Request → CI runs:
```
sqlfluff lint    → enforce SQL style (spacing, casing, aliases)
dbt parse        → validate all ref(), source(), macro references
```
PRs cannot merge until both checks pass.

### On every merge to main → CD runs:
```
sqlfluff lint    → double-check style on merged code
dbt parse        → double-check model references on merged code
deploy           → in production: dbt run + dbt test + trigger Airflow
```

---

##  Dashboard

![Daily Market Overview](docs/stock_analytics_dashboard.pdf)

**Features:**
- KPI cards: Avg Daily Change %, Top Stock, Stocks Up/Down
- Bar chart: all 20 stocks ranked by daily performance
- Sector bar chart: avg change by sector (Consumer, Tech, Healthcare, Finance, Energy)
- Risk vs Return scatter plot: intraday range % vs price change %
- Data table with conditional formatting (green = up, red = down)
- Interactive slicers: Date, Sector

---

## Links

- **GitHub Actions:** [View CI/CD runs](https://github.com/YOUR_USERNAME/stock-analytics-pipeline/actions)

---

## What I Learned

- How to design a **layered data architecture** (raw → staging → marts) and why each layer exists
- How to write **idempotent data pipelines** that can safely re-run without creating duplicates
- How dbt's **ref() and source()** functions create an implicit DAG that enables lineage tracking
- How to write **reusable dbt macros** in Jinja to avoid repeating business logic
- How **Application Default Credentials** work and why they're safer than service account keys
- How to use **Apache Airflow** to orchestrate a multi-step pipeline with retry logic
- How to write **GitHub Actions workflows** that enforce quality gates on every PR
- How **sqlfluff** enforces SQL style consistency the same way black/prettier do for Python/JS
- Why **pinning package versions** in CI is critical for reproducible builds

---

## Author

**Saketh Reddy** — Analytics Engineer Portfolio Project, 2026