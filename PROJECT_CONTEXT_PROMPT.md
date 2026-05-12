# 🚀 Senior Data Engineer Portfolio — Project Context Prompt

## WHO I AM
I am a Data Engineer from Kazakhstan (Astana), building a **Senior Data Engineer portfolio project**.
I am a beginner in Python. I need step-by-step explanations like I have never coded before.
Everything must run **online only** — no local execution except Power BI Desktop.

---

## GOAL
Build a full end-to-end modern data engineering pipeline that demonstrates Senior DE skills:
- Multi-source data collection (REST API, CSV/API, Web Scraping, Event Generator)
- Stream processing (Apache Kafka + Apache Flink)
- Batch processing (Apache Spark / PySpark)
- Data Warehouse with 3-layer architecture (raw → staging → mart)
- Orchestration (Apache Airflow or GitHub Actions)
- Data quality checks (Great Expectations)
- BI dashboards (Power BI)

---

## TECH STACK (DECIDED)

| Layer | Technology | Where it runs |
|-------|-----------|---------------|
| Code repository | GitHub (repo: `de-portfolio`, user: GabYer) | github.com — FREE |
| Automation / Scheduler | GitHub Actions (cron every 6 hours) | github.com — FREE |
| Database / DWH | PostgreSQL 16 on **Neon.tech** | neon.tech — FREE 3GB |
| Batch processing | Apache Spark (PySpark) | Local Docker or Google Colab |
| Stream processing | Apache Kafka + Apache Flink | Docker Compose (future) |
| Orchestration | GitHub Actions now → Apache Airflow later | Docker Compose (future) |
| Transformations | SQL (raw→staging→mart) + dbt (future) | Neon.tech |
| BI / Dashboards | Power BI Desktop | Local PC (connects to Neon) |
| Python libraries | requests, psycopg2-binary, faker, beautifulsoup4, lxml | GitHub Actions runner |

---

## DATA SOURCES (4 TYPES)

### 1. REST API — Financial / Crypto
- **CoinGecko API** — BTC, ETH, BNB prices in USD (free, no key needed)
  - URL: `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,binancecoin`
- **National Bank of Kazakhstan (NBK)** — official KZT exchange rates (USD, EUR, RUB, CNY, GBP)
  - URL: `https://nationalbank.kz/rss/get_rates.cfm?fdate=DD.MM.YYYY`
- **Open-Meteo** — weather data for Astana and Almaty (free, no key)
  - URL: `https://api.open-meteo.com/v1/forecast?latitude=51.18&longitude=71.45&current_weather=true`

### 2. CSV / Open Data Kazakhstan
- **data.egov.kz** — Government open data portal of Kazakhstan
  - Government procurement (tenders, contracts, suppliers)
  - Companies registry
  - API: `https://data.egov.kz/api/v4/{dataset}`
- **stat.gov.kz** — Bureau of National Statistics
  - GDP, inflation, employment, demographic data by regions

### 3. Web Scraping
- **Kolesa.kz** — Kazakhstan's largest car marketplace
  - Data: brand, model, year, mileage, price in KZT, city, transmission, fuel type
  - URL: `https://kolesa.kz/cars/`
  - Tool: BeautifulSoup4 + requests

### 4. Event Generator (Synthetic Streaming Data)
- **Transactions** — fake bank transactions: user_id, amount_kzt, merchant, category, city, channel (mobile/web/pos), status, fraud_flag
- **Clickstream** — fake user behavior: session_id, event_type (page_view/click/purchase), device, city
- **IoT Sensors** — fake sensor telemetry: sensor_id, temperature, humidity, location (Kazakhstan cities)
- Tool: Python `faker` library → writes to PostgreSQL raw tables → later to Kafka topics

---

## DATABASE ARCHITECTURE — Neon.tech PostgreSQL

### Connection Parameters
```
Host: ep-empty-base-alumbcid-pooler.c-3.eu-central-1.aws.neon.tech
Port: 5432
Database: neondb
User: neondb_owner
SSL: require
DATABASE_URL format: postgresql://neondb_owner:PASSWORD@ep-empty-base-alumbcid-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

### Schemas (all already created in Neon)
```
raw.*       — data as-is from sources, never modified
staging.*   — cleaned, typed, deduplicated
mart.*      — aggregated views for Power BI
meta.*      — pipeline monitoring and logging
```

### Key Tables Already Created
```sql
-- RAW layer
raw.crypto_prices          -- CoinGecko data
raw.forex_rates_nbk        -- NBK exchange rates
raw.weather_astana         -- Open-Meteo weather
raw.kz_goszakup            -- Kazakhstan procurement
raw.kz_stat_regions        -- Regional statistics
raw.kz_companies           -- Companies registry
raw.kolesa_listings        -- Car listings scraped
raw.scrape_runs            -- Scraping session log
raw.events_transactions    -- Fake transactions
raw.events_clickstream     -- Fake clickstream
raw.events_iot_sensors     -- Fake IoT sensor data

-- META layer
meta.pipeline_runs         -- logs every pipeline execution
meta.load_watermarks       -- tracks last loaded timestamp per source
meta.source_health         -- API availability checks

-- STAGING & MART
staging.crypto_prices, staging.forex_rates, staging.car_listings, staging.transactions
mart.daily_crypto_kzt, mart.forex_trend, mart.cars_by_brand, mart.txn_hourly, mart.fraud_signals
```

---

## GITHUB REPOSITORY STRUCTURE

```
de-portfolio/                          ← GitHub repo (GabYer/de-portfolio)
├── requirements.txt                   ← ✅ DONE
├── .github/
│   └── workflows/
│       └── ingest.yml                 ← ✅ DONE (runs every 6 hours)
├── ingestion/
│   ├── db.py                          ← ✅ DONE (Neon connection + helpers)
│   ├── run_all.py                     ← ✅ DONE (orchestrates all sources)
│   └── sources/
│       ├── __init__.py                ← ✅ DONE (empty file)
│       ├── crypto_api.py              ← ✅ DONE + TESTED ✓
│       ├── nbk_forex.py               ← ✅ DONE + TESTED ✓
│       ├── weather_api.py             ← ❌ NOT CREATED YET
│       ├── kz_egov.py                 ← ❌ NOT CREATED YET
│       ├── kolesa_scraper.py          ← ❌ NOT CREATED YET
│       └── event_generator.py         ← ❌ NOT CREATED YET
└── sql/
    └── 01_create_schemas.sql          ← ✅ DONE (all DDL)
```

---

## CURRENT STATUS — What's Done ✅

1. ✅ Neon.tech PostgreSQL — registered, all schemas and tables created
2. ✅ GitHub repository `de-portfolio` created (user: GabYer)
3. ✅ `requirements.txt` — in repo root
4. ✅ `ingestion/db.py` — Neon connection helper
5. ✅ `ingestion/run_all.py` — main runner (currently runs crypto + forex)
6. ✅ `ingestion/sources/__init__.py` — empty module file
7. ✅ `ingestion/sources/crypto_api.py` — fetches BTC/ETH/BNB → raw.crypto_prices
8. ✅ `ingestion/sources/nbk_forex.py` — fetches KZT rates → raw.forex_rates_nbk
9. ✅ `.github/workflows/ingest.yml` — GitHub Actions cron every 6h
10. ✅ `DATABASE_URL` secret added to GitHub Secrets
11. ✅ **First pipeline run: SUCCESS** (21 seconds, Status: Success)
12. ✅ Data confirmed in Neon tables

---

## WHAT NEEDS TO BE DONE NEXT ❌

### Immediate next steps (in order):

**Step A — Complete remaining sources (create files in GitHub browser)**
- `ingestion/sources/weather_api.py` — Open-Meteo for Astana + Almaty
- `ingestion/sources/kz_egov.py` — data.egov.kz procurement + companies
- `ingestion/sources/kolesa_scraper.py` — Kolesa.kz web scraper
- `ingestion/sources/event_generator.py` — Faker transactions + clickstream + IoT
- Update `ingestion/run_all.py` to import and call all 4 new sources

**Step B — Staging transformations**
- SQL script to populate staging.* tables from raw.* (dedup, type casting, normalization)
- Run after each ingestion via GitHub Actions

**Step C — Power BI connection**
- Connect Power BI Desktop to Neon PostgreSQL
- Build dashboards from mart.* views:
  - Crypto prices in KZT over time
  - NBK exchange rate trends
  - Kazakhstan car market (Kolesa.kz) analysis
  - Transaction fraud signals
  - Regional statistics map

**Step D — Advanced DE components (future)**
- Apache Kafka + Apache Flink for real streaming (Docker Compose)
- Apache Airflow DAGs replacing GitHub Actions
- dbt models for transformations
- Great Expectations for data quality
- Apache Spark for batch processing of large datasets
- Grafana + Prometheus monitoring dashboard

---

## IMPORTANT RULES FOR THIS PROJECT

1. **User is a Python beginner** — explain every step like they have never coded
2. **Everything runs online** — no local Python/terminal needed
3. **Files are created directly in GitHub browser** — no git clone, no local IDE
4. **One file at a time** — show code for one file, wait for confirmation, then next
5. **Always show full file content** — never show partial code snippets
6. **GitHub Actions = the robot** that runs Python code on a schedule automatically
7. **Neon.tech = the database** in the cloud, accessible from anywhere
8. **DATABASE_URL is stored in GitHub Secrets** — never hardcode passwords

---

## HOW TO CONTINUE THIS PROJECT

When continuing this project with any AI assistant, say:

> "I am continuing my Senior Data Engineer portfolio project. Read the context above.
> The pipeline is working (crypto + forex ingestion runs every 6 hours via GitHub Actions → Neon PostgreSQL).
> Next step is: [describe what you want to do]"

### Example continuation prompts:
- "Create the weather_api.py file for Open-Meteo"
- "Create the event_generator.py file with Faker"
- "Create the kolesa_scraper.py file for Kolesa.kz"
- "Write the staging transformation SQL"
- "Help me connect Power BI to Neon"
- "Set up Apache Kafka with Docker Compose"

---

## FINAL PORTFOLIO RESULT (end goal)

A GitHub repository demonstrating:
- **4 data sources** collected automatically every 6 hours
- **3-layer DWH** (raw / staging / mart) in PostgreSQL
- **Streaming pipeline** with Kafka + Flink
- **Batch processing** with PySpark
- **Orchestration** with Airflow
- **Data quality** with Great Expectations
- **BI dashboards** in Power BI showing Kazakhstan financial and market data
- **Full monitoring** with pipeline run logs
- Professional README with architecture diagram

This proves Senior Data Engineer skills to any recruiter or employer.
