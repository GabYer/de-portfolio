```
                    /$$$$$$            /$$     /$$     /$$                 
                   /$$__  $$          | $$    |  $$   /$$/                 
                  | $$  \__/  /$$$$$$ | $$$$$$$\  $$ /$$//$$$$$$   /$$$$$$ 
                  | $$ /$$$$ |____  $$| $$__  $$\  $$$$//$$__  $$ /$$__  $$
                  | $$|_  $$  /$$$$$$$| $$  \ $$ \  $$/| $$$$$$$$| $$  \__/
                  | $$  \ $$ /$$__  $$| $$  | $$  | $$ | $$_____/| $$      
                  |  $$$$$$/|  $$$$$$$| $$$$$$$/  | $$ |  $$$$$$$| $$      
                   \______/  \_______/|_______/   |__/  \_______/|__/      
```

# 🇰🇿 Kazakhstan Data Engineering Portfolio

> **End-to-end data platform** — real-time Binance streaming, 8 data sources,
> PostgreSQL DWH, Apache Kafka, ClickHouse OLAP, Airflow orchestration,
> dbt transformations, Grafana monitoring — all running on a homelab server,
> publicly accessible via **gabyer.dev**

[![Airflow](https://img.shields.io/badge/Airflow-airflow.gabyer.dev-017CEE?logo=apacheairflow)](https://airflow.gabyer.dev)
[![Grafana](https://img.shields.io/badge/Grafana-grafana.gabyer.dev-F46800?logo=grafana)](https://grafana.gabyer.dev)
[![Kafka](https://img.shields.io/badge/Kafka-kafka.gabyer.dev-231F20?logo=apachekafka)](https://kafka.gabyer.dev)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-clickhouse.gabyer.dev-FFCC01?logo=clickhouse)](https://clickhouse.gabyer.dev)
[![Portfolio](https://img.shields.io/badge/Portfolio-portfolio.gabyer.dev-orange?logo=vercel)](https://portfolio.gabyer.dev)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
│                                                                     │
│  CoinGecko   НБК Kazakhstan   Open-Meteo   Tengrinews.kz            │
│  REST API      REST API        REST API      Web Scraping           │
│                                                                     │
│         Faker Event Generator          Binance WebSocket            │
│     (transactions/clicks/IoT)        (BTC/ETH/BNB/SOL/XRP)         │
└──────────────┬──────────────────────────────┬───────────────────────┘
               │                              │ ~70 trades/sec 24/7
               ▼                              ▼
┌──────────────────────────┐    ┌─────────────────────────────────────┐
│   HOMELAB SERVER         │    │         CLICKHOUSE OLAP             │
│   Ubuntu 24.04 · i5      │    │                                     │
│   16GB RAM · 500Mb/s     │    │  trading.binance_trades (25M+)      │
│                          │    │  trading.mv_vwap_1min (MAT VIEW)    │
│  ┌─────────────────────┐ │    │  trading.mv_buysell_1min (MAT VIEW) │
│  │  Apache Airflow     │ │    └─────────────────────────────────────┘
│  │  DAG every 6 hours  │ │
│  │  git_pull           │ │
│  │  ingest_all_sources │ │
│  │  binance_realtime   │ │
│  │  staging_transform  │ │    ← dbt run (docker container)
│  └─────────────────────┘ │
│                          │
│  ┌─────────────────────┐ │
│  │   Apache Kafka      │ │
│  │   transactions      │ │
│  │   clickstream       │ │
│  │   iot_sensors       │ │
│  └─────────────────────┘ │
│                          │
│  ┌─────────────────────┐ │
│  │  Binance 24/7       │ │
│  │  Docker Container   │ │
│  │  restart: always    │ │
│  └─────────────────────┘ │
└──────────────┬───────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PostgreSQL DWH — Neon.tech                         │
│                                                                     │
│  raw.*  →  dbt staging.*  →  dbt mart.*      meta.pipeline_runs     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
┌──────────────────────┐         ┌─────────────────────────┐
│   Apache Superset    │         │        Grafana           │
│   Railway.app        │         │   grafana.gabyer.dev     │
│   BI Dashboards      │         │   Pipeline Monitor       │
│                      │         │   Binance Real-time      │
└──────────────────────┘         │   Storage Monitoring     │
               │                 └─────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              portfolio.gabyer.dev (Next.js · Vercel)                │
│         Live pipeline visualization · Crypto prices · News          │
└─────────────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Cloudflare Tunnel — gabyer.dev                         │
│  airflow · grafana · kafka · clickhouse — all HTTPS, no open ports  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🌐 Live Services

| Service | URL | Purpose |
|---------|-----|---------|
| Portfolio | [portfolio.gabyer.dev](https://portfolio.gabyer.dev) | Live data website |
| Apache Airflow | [airflow.gabyer.dev](https://airflow.gabyer.dev) | Pipeline orchestration |
| Grafana | [grafana.gabyer.dev](https://grafana.gabyer.dev) | Monitoring & alerts |
| Kafka UI | [kafka.gabyer.dev](https://kafka.gabyer.dev) | Stream inspection |
| ClickHouse UI | [clickhouse.gabyer.dev](https://clickhouse.gabyer.dev) | OLAP queries |
| Superset | [superset-production-0c30.up.railway.app](https://superset-production-0c30.up.railway.app) | BI dashboards |

---

## 🛠️ Tech Stack

| Layer | Technology | Where |
|-------|-----------|-------|
| Ingestion | Python 3.12 | Homelab · Airflow |
| Streaming | Apache Kafka + Zookeeper | Homelab · Docker |
| Real-time | Binance WebSocket 24/7 | Homelab · Docker (restart: always) |
| Orchestration | Apache Airflow 2.9.0 | Homelab · Docker |
| Transformation | dbt (data build tool) | Homelab · Docker |
| OLAP | ClickHouse 24.3 | Homelab · Docker |
| DWH | PostgreSQL 16 (Neon.tech) | Cloud · FREE |
| BI | Apache Superset | Railway.app · FREE |
| Monitoring | Grafana + Prometheus + Node Exporter | Homelab · Docker |
| Container mgmt | Portainer CE | Homelab · Docker |
| Tunnel | Cloudflare Tunnel | gabyer.dev · FREE |
| Zero Trust | Cloudflare Access (email OTP) | gabyer.dev · FREE |
| Backup | rclone → Google Drive (7 days) | Cloud · FREE |
| CI/CD | GitHub Actions + self-hosted runner | github.com · FREE |
| Website | Next.js · Vercel | portfolio.gabyer.dev · FREE |

---

## 📊 Data Sources

| # | Source | Type | Data | Table |
|---|--------|------|------|-------|
| 1 | CoinGecko API | REST API | BTC/ETH/BNB prices USD | `raw.crypto_prices` |
| 2 | НБК Kazakhstan | REST API | USD/EUR/RUB/CNY/GBP → KZT | `raw.forex_rates_nbk` |
| 3 | Open-Meteo | REST API | Weather: Astana/Almaty/Shymkent | `raw.weather_astana` |
| 4 | Faker Generator | Event Gen | Transactions/clicks/IoT | `raw.events_*` |
| 5 | Tengrinews.kz | Web Scraping | Kazakhstan news | `raw.tengri_news` |
| 6 | Kafka Producer | Streaming | Events → Kafka topics | — |
| 7 | Kafka Consumer | Streaming | Kafka → Neon | `raw.events_*` |
| 8 | Binance WebSocket | Real-time 24/7 | BTC/ETH/BNB/SOL/XRP trades | `trading.binance_trades` |

---

## 🌊 Real-time Streaming

```
Binance WebSocket (wss://stream.binance.com)
        │  ~70 trades/second · 24/7 · auto-reconnect
        ▼
binance_stream.py (Docker · restart: always)
        │
        ├──► trading.binance_trades (ReplacingMergeTree — dedup by trade_id)
        │    25M+ rows · 282MB compressed
        │
        ├──► trading.mv_vwap_1min (auto via Materialized View)
        │    VWAP = sum(price×qty) / sum(qty) per minute per symbol
        │
        └──► trading.mv_buysell_1min (auto via Materialized View)
             buy_volume vs sell_volume per minute
```

---

## 🗄️ DWH Schema (dbt)

```
raw.*                          staging.*  (dbt tables)
├── crypto_prices              ├── stg_crypto_prices   (deduped by hour)
├── forex_rates_nbk            ├── stg_forex_rates     (deduped by date)
├── weather_astana             ├── stg_transactions    (deduped by event_id)
├── events_transactions        └── stg_news            (deduped by url)
├── events_clickstream
├── events_iot_sensors         mart.*  (dbt views)
└── tengri_news                ├── mart_daily_crypto_kzt
                               ├── mart_forex_trend
meta.*                         ├── mart_txn_hourly
├── pipeline_runs              ├── mart_fraud_signals
├── load_watermarks            └── mart_news_by_category
└── source_health
```

---

## ⚙️ Airflow Pipeline

```
de_portfolio_ingestion — every 6 hours
│
├── git_pull              — pulls latest code from GitHub (auto-deploy)
├── ingest_all_sources    — runs all 7 batch sources → Neon
├── binance_realtime      — 60s Binance WebSocket → ClickHouse (~4000 trades)
└── staging_transform     — dbt run (docker run dbt-dbt:latest)
                            raw.* → staging.stg_* → mart.mart_*
                            PASS=9 WARN=0 ERROR=0 in ~9 seconds
```

---

## 📊 Grafana Dashboards

```
Node Exporter Full      — CPU, RAM, disk /, disk /data, network
Storage Monitoring      — Neon schema sizes, top tables, ClickHouse binance_trades
Binance Real-Time       — BTC price history, all symbols, trades/min, 24h volume
```

---

## 🚀 CI/CD

```
git push → GitHub Actions (self-hosted runner on homelab)
         → deploy.yml
           ├── sudo chmod -R 777 /data/de-portfolio
           ├── git reset --hard origin/main
           └── git pull origin main

         → Vercel (portfolio-website repo)
           └── auto-deploy to portfolio.gabyer.dev
```

---

## 📁 Project Structure

```
de-portfolio/
├── .github/workflows/
│   ├── deploy.yml          # auto-deploy on push (self-hosted runner)
│   ├── ingest.yml          # manual only
│   ├── transform.yml       # manual only
│   └── migrate.yml         # manual DDL
├── dags/
│   └── de_portfolio_ingestion.py
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── macros/
│   │   └── generate_schema_name.sql
│   └── models/
│       ├── sources.yml
│       ├── staging/
│       │   ├── stg_crypto_prices.sql
│       │   ├── stg_forex_rates.sql
│       │   ├── stg_transactions.sql
│       │   └── stg_news.sql
│       └── mart/
│           ├── mart_daily_crypto_kzt.sql
│           ├── mart_forex_trend.sql
│           ├── mart_txn_hourly.sql
│           ├── mart_fraud_signals.sql
│           └── mart_news_by_category.sql
├── ingestion/
│   ├── db.py
│   ├── run_all.py
│   └── sources/
│       ├── crypto_api.py
│       ├── nbk_forex.py
│       ├── weather_api.py
│       ├── event_generator.py
│       ├── tengri_scraper.py
│       ├── kafka_producer.py
│       ├── kafka_consumer.py
│       ├── binance_consumer.py   ← DAG task (60s)
│       └── binance_stream.py     ← 24/7 Docker container
├── sql/migrations/
│   ├── 001_init_schemas.sql
│   └── 002_staging_transform.sql  ← legacy, replaced by dbt
├── docs/
│   └── TECH_DEBT.md
└── requirements.txt
```

---

## 🗺️ Roadmap

- [x] Multi-source ingestion (8 sources)
- [x] PostgreSQL DWH (raw / staging / mart)
- [x] Apache Kafka streaming (producer + consumer)
- [x] Binance WebSocket real-time → ClickHouse OLAP
- [x] ClickHouse Materialized Views (VWAP, Buy/Sell pressure)
- [x] Apache Airflow orchestration (homelab)
- [x] Database migrations via Git
- [x] BI Dashboards (Apache Superset)
- [x] Grafana monitoring (Node Exporter, Storage, Binance Real-Time)
- [x] Homelab server (Ubuntu + Docker)
- [x] Cloudflare Tunnel (gabyer.dev — all services public HTTPS)
- [x] Cloudflare Zero Trust (email OTP on all services)
- [x] Automated backup → Google Drive (7 days retention)
- [x] fstab auto-mount (/data disk)
- [x] **Binance 24/7 continuous streaming** (Docker · restart: always · auto-reconnect)
- [x] **dbt transformations** (9 models · staging + mart · integrated with Airflow)
- [x] **CI/CD auto-deploy** (GitHub Actions · self-hosted runner · git pull on push)
- [x] **Portfolio website** (Next.js · Vercel · portfolio.gabyer.dev)
- [ ] dbt compile check in CI/CD (before deploy)
- [ ] Apache Spark (batch processing)
- [ ] Great Expectations (data quality)
- [ ] AI Self-Healing Agent (on_failure_callback + Claude API + Telegram)

---

## 👤 Author

**GabYer** — Data Engineer, Astana, Kazakhstan

[![GitHub](https://img.shields.io/badge/GitHub-GabYer-black?logo=github)](https://github.com/GabYer)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-gabyer-blue?logo=linkedin)](https://www.linkedin.com/in/gabyer/)
[![Email](https://img.shields.io/badge/Email-gyermekbayev@gmail.com-red?logo=gmail)](mailto:gyermekbayev@gmail.com)
[![Domain](https://img.shields.io/badge/Domain-gabyer.dev-orange?logo=cloudflare)](https://gabyer.dev)
[![Portfolio](https://img.shields.io/badge/Portfolio-portfolio.gabyer.dev-blue?logo=vercel)](https://portfolio.gabyer.dev)
