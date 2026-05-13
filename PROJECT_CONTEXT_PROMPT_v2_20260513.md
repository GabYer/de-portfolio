# 🚀 Senior Data Engineer Portfolio — Project Context Prompt
## Version: 2026-05-12 | Stage: Ingestion Layer 80% Complete

---

## WHO I AM
- Data Engineer from **Kazakhstan (Astana)**
- **Python beginner** — explain every step like I have never coded before
- Everything runs **online only** — no local execution except Power BI Desktop
- Files are created and edited **directly in GitHub browser** — no terminal, no git clone

---

## GOAL
Build a full end-to-end modern data pipeline that demonstrates **Senior Data Engineer** skills:
- Multi-source data collection (REST API, CSV/API, Web Scraping, Event Generator)
- Stream processing (Apache Kafka + Apache Flink)
- Batch processing (Apache Spark / PySpark)
- 3-layer Data Warehouse architecture (raw → staging → mart)
- Orchestration (GitHub Actions now → Apache Airflow later)
- Data quality (Great Expectations)
- BI dashboards (Power BI Desktop)

---

## TECH STACK

| Layer | Technology | Where |
|-------|-----------|-------|
| Code repository | GitHub repo: `de-portfolio`, user: `GabYer` | github.com FREE |
| Automation / Scheduler | GitHub Actions (cron every 6 hours) | github.com FREE |
| Database / DWH | PostgreSQL 16 — **Neon.tech** | neon.tech FREE 3GB |
| Transformations | SQL (raw → staging → mart) | Neon.tech |
| Batch processing | Apache Spark / PySpark | Docker (future) |
| Stream processing | Apache Kafka + Flink | Docker (future) |
| Orchestration | GitHub Actions → Apache Airflow (future) | Docker (future) |
| BI Dashboards | Power BI Desktop | Local PC → connects to Neon |
| Python libs | requests, psycopg2-binary, faker, beautifulsoup4, lxml | GitHub Actions runner |

---

## NEON DATABASE CONNECTION

```
Host:     ep-empty-base-alumbcid-pooler.c-3.eu-central-1.aws.neon.tech
Port:     5432
Database: neondb
User:     neondb_owner
SSL:      require
DATABASE_URL: postgresql://neondb_owner:PASSWORD@ep-empty-base-alumbcid-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require
```
> DATABASE_URL is stored in **GitHub Secrets** (never hardcoded)

---

## DATA SOURCES — 5 ACTIVE

### 1. ✅ CoinGecko REST API — Crypto prices
- BTC, ETH, BNB prices in USD
- URL: `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,binancecoin`
- Target table: `raw.crypto_prices`
- File: `ingestion/sources/crypto_api.py`
- Status: **WORKING** — 3 rows per run

### 2. ✅ National Bank of Kazakhstan (NBK) — Forex rates
- Official KZT rates: USD=461.26, EUR=542.58, RUB=6.18, CNY=67.82, GBP=627.41
- URL: `https://nationalbank.kz/rss/get_rates.cfm?fdate=DD.MM.YYYY`
- Target table: `raw.forex_rates_nbk`
- File: `ingestion/sources/nbk_forex.py`
- Status: **WORKING** — 5 rows per run

### 3. ⚠️ Open-Meteo — Weather (Astana, Almaty, Shymkent)
- Temperature, humidity, wind, precipitation for Kazakhstan cities
- URL: `https://api.open-meteo.com/v1/forecast?latitude=...`
- Target table: `raw.weather_astana`
- File: `ingestion/sources/weather_api.py`
- Status: **PARTIAL** — timeout issues on Astana and Shymkent (only Almaty loads)
- Fix needed: increase timeout from 15s → 30s, add retry logic

### 4. ✅ Event Generator — Synthetic streaming events (Faker)
- Transactions: 50 rows (user_id, amount_kzt, merchant, category, city, channel, fraud_flag)
- Clickstream: 80 rows (session_id, event_type, device, city)
- IoT sensors: 30 rows (sensor_id, temperature/humidity/pressure, Kazakhstan cities)
- Target tables: `raw.events_transactions`, `raw.events_clickstream`, `raw.events_iot_sensors`
- File: `ingestion/sources/event_generator.py`
- Status: **WORKING** — 160 rows per run

### 5. ⚠️ Tengrinews.kz — Web scraping (Kazakhstan news portal)
- Sections: Новости, Экономика, Спорт
- Data: url, title, category, published_at
- Target table: `raw.tengri_news` (with UNIQUE url constraint)
- File: `ingestion/sources/tengri_scraper.py`
- Status: **PARTIAL** — Экономика works (30 rows), Новости and Спорт return 0
- Fix needed: URL regex pattern doesn't match /news/ and /sport/ sections

---

## DATABASE ARCHITECTURE — Neon PostgreSQL

### Schemas (all created)
```
raw.*       — data as-is from all sources
staging.*   — cleaned, typed, deduplicated
mart.*      — aggregated views for Power BI
meta.*      — pipeline run logs and monitoring
```

### All Tables Created
```sql
-- RAW
raw.crypto_prices           raw.forex_rates_nbk
raw.weather_astana          raw.kz_goszakup
raw.kz_stat_regions         raw.kz_companies
raw.kolesa_listings         raw.scrape_runs
raw.events_transactions     raw.events_clickstream
raw.events_iot_sensors      raw.tengri_news

-- STAGING
staging.crypto_prices       staging.forex_rates
staging.car_listings        staging.transactions

-- MART (Views)
mart.daily_crypto_kzt       mart.forex_trend
mart.cars_by_brand          mart.txn_hourly
mart.fraud_signals

-- META
meta.pipeline_runs          meta.load_watermarks
meta.source_health
```

---

## GITHUB REPOSITORY STRUCTURE

```
de-portfolio/
├── requirements.txt                        ✅ DONE
├── PROJECT_CONTEXT_PROMPT.md               ✅ DONE (this file)
├── .github/
│   └── workflows/
│       └── ingest.yml                      ✅ DONE — cron every 6h
├── ingestion/
│   ├── db.py                               ✅ DONE
│   ├── run_all.py                          ✅ DONE (5 sources)
│   └── sources/
│       ├── __init__.py                     ✅ DONE
│       ├── crypto_api.py                   ✅ DONE ✓ TESTED
│       ├── nbk_forex.py                    ✅ DONE ✓ TESTED
│       ├── weather_api.py                  ⚠️  DONE — timeout fix needed
│       ├── event_generator.py              ✅ DONE ✓ TESTED
│       └── tengri_scraper.py               ⚠️  DONE — selector fix needed
└── sql/
    └── 01_create_schemas.sql               ✅ DONE
```

---

## PIPELINE RUNS LOG (latest)

```
pipeline_name     status   rows  time
─────────────────────────────────────
crypto            success  3     ~2s
forex_nbk         success  5     ~3s
weather           partial  1     ~40s  ← timeout issue
event_generator   success  160   ~2s
tengri_scraper    partial  30    ~6s   ← selector issue
```
**Total per run: ~199 rows in ~60 seconds**
**Runs automatically every 6 hours via GitHub Actions** ✅

---

## KNOWN ISSUES TO FIX (next session)

### Fix 1 — weather_api.py timeout
File: `ingestion/sources/weather_api.py`
Problem: `Read timed out` on Astana and Shymkent
Fix: Change `timeout=15` → `timeout=30` and add retry loop

### Fix 2 — tengri_scraper.py selectors
File: `ingestion/sources/tengri_scraper.py`
Problem: `/news/` and `/sport/` sections return 0 — URL regex too strict
Current regex: `/(kazakhstan_news|world_news|economics_business|sport|...)/[a-z0-9_-]+-\d+`
Fix: The `/news/` section uses different URL patterns like `/kazakhstan_news/` and `/world_news/`
The section URL `/news/` already captures mixed categories — adjust regex to catch all article URLs

---

## WHAT'S NEXT (in order)

### Step 1 — Fix weather + tengri (quick fixes)
- weather_api.py: timeout 15 → 30, add retry
- tengri_scraper.py: fix regex for /news/ and /sport/ sections

### Step 2 — Add Kazakhstan open data sources
- `ingestion/sources/kz_egov.py` — data.egov.kz REST API (companies, procurement)
- `ingestion/sources/kz_goszakup.py` — goszakup.gov.kz GraphQL API (tenders, contracts)

### Step 3 — Staging transformations
- SQL: raw → staging (deduplication, type casting, normalization)
- Run after ingestion via GitHub Actions

### Step 4 — Power BI connection
- Connect Power BI Desktop to Neon (host above)
- Build dashboards from mart.* views

### Step 5 — Advanced DE (Docker Compose stack)
- Apache Kafka + Flink (real streaming)
- Apache Airflow (replace GitHub Actions)
- dbt (replace raw SQL transforms)
- Great Expectations (data quality)
- Grafana + Prometheus (monitoring)

---

## RULES FOR THIS PROJECT

1. User is a **Python beginner** — explain every step simply
2. **Everything online** — no local Python/terminal
3. Files created in **GitHub browser only**
4. Show **full file content** always — never partial snippets
5. **One file at a time** — wait for confirmation before next
6. **Never hardcode passwords** — use GitHub Secrets
7. GitHub Actions = robot that runs Python on schedule
8. Neon.tech = PostgreSQL database in the cloud

---

## HOW TO CONTINUE WITH ANY AI

Paste this entire file and say:

> "This is my Senior DE portfolio project context.
> Currently: ingestion pipeline runs every 6h via GitHub Actions → Neon PostgreSQL.
> 5 sources active (crypto, forex, weather, events, tengri news scraper).
> Next step: [what you want to do]"

### Ready-to-use continuation prompts:
- "Fix the weather_api.py timeout issue"
- "Fix tengri_scraper.py to get Новости and Спорт sections"
- "Create kz_egov.py for data.egov.kz"
- "Write the staging transformation SQL"
- "Help me connect Power BI to Neon"
- "Set up Docker Compose with Kafka + Flink + Airflow"
- "Create dbt models for staging layer"
