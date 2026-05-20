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
> Grafana monitoring — all running on a homelab server, publicly accessible via **gabyer.dev**

[![Airflow](https://img.shields.io/badge/Airflow-airflow.gabyer.dev-017CEE?logo=apacheairflow)](https://airflow.gabyer.dev)
[![Grafana](https://img.shields.io/badge/Grafana-grafana.gabyer.dev-F46800?logo=grafana)](https://grafana.gabyer.dev)
[![Kafka](https://img.shields.io/badge/Kafka-kafka.gabyer.dev-231F20?logo=apachekafka)](https://kafka.gabyer.dev)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-clickhouse.gabyer.dev-FFCC01?logo=clickhouse)](https://clickhouse.gabyer.dev)

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
               │                              │ ~70 trades/sec
               ▼                              ▼
┌──────────────────────────┐    ┌─────────────────────────────────────┐
│   HOMELAB SERVER         │    │         CLICKHOUSE OLAP             │
│   Ubuntu 24.04 · i5      │    │                                     │
│   16GB RAM · 500Mb/s     │    │  trading.binance_trades             │
│                          │    │  trading.mv_vwap_1min (MAT VIEW)    │
│  ┌─────────────────────┐ │    │  trading.mv_buysell_1min (MAT VIEW) │
│  │  Apache Airflow     │ │    └─────────────────────────────────────┘
│  │  DAG every 6 hours  │ │
│  │  git_pull           │ │
│  │  ingest_all_sources │ │
│  │  binance_realtime   │ │
│  │  staging_transform  │ │
│  └─────────────────────┘ │
│                          │
│  ┌─────────────────────┐ │
│  │   Apache Kafka      │ │
│  │   transactions      │ │
│  │   clickstream       │ │
│  │   iot_sensors       │ │
│  └─────────────────────┘ │
└──────────────┬───────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PostgreSQL DWH — Neon.tech                         │
│                                                                     │
│  raw.*  →  staging.*  →  mart.*          meta.pipeline_runs         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
┌──────────────────────┐         ┌─────────────────────────┐
│   Apache Superset    │         │        Grafana           │
│   Railway.app        │         │   grafana.gabyer.dev     │
│   BI Dashboards      │         │   Pipeline Monitor       │
│                      │         │   Binance Real-time      │
└──────────────────────┘         └─────────────────────────┘
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
| Real-time | Binance WebSocket | Homelab · Airflow |
| Orchestration | Apache Airflow 2.9.0 | Homelab · Docker |
| OLAP | ClickHouse 24.3 | Homelab · Docker |
| DWH | PostgreSQL 16 (Neon.tech) | Cloud · FREE |
| BI | Apache Superset | Railway.app · FREE |
| Monitoring | Grafana | Homelab · Docker |
| Container mgmt | Portainer CE | Homelab · Docker |
| Tunnel | Cloudflare Tunnel | gabyer.dev · FREE |
| Backup | rclone → Google Drive | Cloud · FREE |
| CI/CD | GitHub Actions | github.com · FREE |

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
| 8 | Binance WebSocket | Real-time | BTC/ETH/BNB/SOL/XRP trades | `trading.binance_trades` |

---

## 🌊 Real-time Streaming

```
Binance WebSocket (wss://stream.binance.com)
        │  ~70 trades/second
        ▼
binance_consumer.py
        │
        ├──► trading.binance_trades (ReplacingMergeTree — dedup by trade_id)
        │
        ├──► trading.mv_vwap_1min (auto via Materialized View)
        │    VWAP = sum(price×qty) / sum(qty) per minute per symbol
        │
        └──► trading.mv_buysell_1min (auto via Materialized View)
             buy_volume vs sell_volume per minute
```

---

## 🗄️ DWH Schema

```
raw.*                          staging.*
├── crypto_prices              ├── crypto_prices   (deduped by hour)
├── forex_rates_nbk            ├── forex_rates     (deduped by date)
├── weather_astana             ├── transactions    (deduped by event_id)
├── events_transactions        └── news            (deduped by url)
├── events_clickstream
├── events_iot_sensors         mart.*
└── tengri_news                ├── daily_crypto_kzt
                               ├── forex_trend
meta.*                         ├── txn_hourly
├── pipeline_runs              ├── fraud_signals
├── load_watermarks            └── news_by_category
└── source_health
```

---

## ⚙️ Airflow Pipeline

```
de_portfolio_ingestion — every 6 hours
│
├── git_pull              — pulls latest code from GitHub
├── ingest_all_sources    — runs all 7 batch sources → Neon
├── binance_realtime      — 60s Binance WebSocket → ClickHouse (~4000 trades)
└── staging_transform     — raw.* → staging.* (dedup, clean, typed)
```

---

## 📁 Project Structure

```
de-portfolio/
├── .github/workflows/
│   ├── ingest.yml          # manual only
│   ├── transform.yml       # manual only
│   └── migrate.yml         # manual DDL
├── dags/
│   └── de_portfolio_ingestion.py
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
│       └── binance_consumer.py
├── sql/migrations/
│   ├── 001_init_schemas.sql
│   └── 002_staging_transform.sql
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
- [x] Grafana monitoring (pipeline + real-time)
- [x] Homelab server (Ubuntu + Docker)
- [x] Cloudflare Tunnel (gabyer.dev — all services public HTTPS)
- [x] Automated backup → Google Drive
- [ ] Binance 24/7 continuous streaming (long-running Docker service)
- [ ] Apache Spark (batch processing)
- [ ] dbt (transformations as code)
- [ ] Great Expectations (data quality)
- [ ] AI Self-Healing Agent (on_failure_callback + Claude API + Telegram)
- [ ] Portfolio website on gabyer.dev

---

## 👤 Author

**GabYer** — Data Engineer, Astana, Kazakhstan

[![GitHub](https://img.shields.io/badge/GitHub-GabYer-black?logo=github)](https://github.com/GabYer)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-gabyer-blue?logo=linkedin)](https://www.linkedin.com/in/gabyer/)
[![Email](https://img.shields.io/badge/Email-gyermekbayev@gmail.com-red?logo=gmail)](mailto:gyermekbayev@gmail.com)
[![Domain](https://img.shields.io/badge/Domain-gabyer.dev-orange?logo=cloudflare)](https://gabyer.dev)
