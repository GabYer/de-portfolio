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

> **End-to-end data pipeline** — автоматический сбор данных из 7 источников,
> real-time streaming через Apache Kafka, PostgreSQL DWH с 3-слойной архитектурой,
> Apache Airflow оркестрация на homelab сервере и BI дашборды онлайн.

[![Data Ingestion](https://github.com/GabYer/de-portfolio/actions/workflows/ingest.yml/badge.svg)](https://github.com/GabYer/de-portfolio/actions/workflows/ingest.yml)
[![Staging Transform](https://github.com/GabYer/de-portfolio/actions/workflows/transform.yml/badge.svg)](https://github.com/GabYer/de-portfolio/actions/workflows/transform.yml)

---

## [=] Архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
│                                                                     │
│  CoinGecko API   НБК Казахстан   Open-Meteo   Tengrinews.kz         │
│  (BTC/ETH/BNB)   (KZT курсы)     (погода)     (новости)             │
│                                                                     │
│              Event Generator (Faker)                                │
│         (транзакции / клики / IoT датчики)                          │
└────────────────────────┬────────────────────────────────────────────┘
                         │  Python ingestion scripts
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    HOMELAB SERVER                                   │
│              Ubuntu 24.04 LTS · i5 · 16GB RAM                       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              Apache Airflow 2.9.0                           │    │
│  │   DAG: git_pull → ingest_all_sources → staging_transform    │    │
│  │                  Schedule: every 6 hours                    │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│                             │                                       │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │                  Apache Kafka                               │    │
│  │   topics: transactions · clickstream · iot_sensors          │    │
│  │   Producer → Kafka → Consumer → Neon PostgreSQL             │    │
│  └─────────────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                PostgreSQL DWH — Neon.tech                           │
│                                                                     │
│  ┌──────────┐    ┌───────────┐    ┌──────────────────────────┐      │
│  │  raw.*   │ →  │ staging.* │ →  │         mart.*           │      │
│  │          │    │           │    │                          │      │
│  │ as-is    │    │ cleaned   │    │ daily_crypto_kzt         │      │
│  │ data     │    │ deduped   │    │ forex_trend              │      │
│  │          │    │ typed     │    │ txn_hourly               │      │
│  └──────────┘    └───────────┘    │ fraud_signals            │      │
│                                   │ news_by_category         │      │
│  meta.pipeline_runs (logs)        └──────────────────────────┘      │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Apache Superset — Railway.app                          │
│                                                                     │
│  📈 Крипто в KZT   💱 Курсы валют   🛒 Транзакции                  │
│  📰 Новости КЗ     🚨 Fraud Signals                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## [Т] Стек технологий


| Слой | Технология | Где работает |
|------|-----------|-------------|
| Ingestion | Python 3.12 | Homelab · Airflow container |
| Streaming | Apache Kafka + Zookeeper | Homelab · Docker |
| Orchestration | Apache Airflow 2.9.0 | Homelab · Docker |
| Database | PostgreSQL 16 (Neon.tech) | Cloud · FREE |
| Migrations | psql + SQL files | GitHub Actions (manual) |
| BI | Apache Superset | Railway.app · FREE |
| Container mgmt | Portainer CE | Homelab · Docker |
| Remote access | Tailscale VPN | Homelab |
| CI/CD | GitHub Actions | github.com · FREE |

---

## (->) Источники данных

| # | Источник | Тип | Данные | Таблица |
|---|---------|-----|--------|---------|
| 1 | CoinGecko API | REST API | BTC, ETH, BNB цены в USD | `raw.crypto_prices` |
| 2 | НБК Казахстан | REST API | USD/EUR/RUB/CNY/GBP → KZT | `raw.forex_rates_nbk` |
| 3 | Open-Meteo | REST API | Погода: Астана, Алматы, Шымкент | `raw.weather_astana` |
| 4 | Faker Generator | Event Gen | Транзакции, клики, IoT | `raw.events_*` |
| 5 | Tengrinews.kz | Web Scraping | Новости Казахстана | `raw.tengri_news` |
| 6 | Kafka Producer | Streaming | Events → Kafka topics | — |
| 7 | Kafka Consumer | Streaming | Kafka topics → Neon | `raw.events_*` |

---

## 🌊 Kafka Streaming

```
Faker Events
     │
     ▼
kafka_producer.py
     │
     ├──► topic: transactions  (50 events/run)
     ├──► topic: clickstream   (80 events/run)
     └──► topic: iot_sensors   (30 events/run)
                │
                ▼
        kafka_consumer.py
                │
                ├──► raw.events_transactions
                ├──► raw.events_clickstream
                └──► raw.events_iot_sensors
```

---

## [DB] Схема базы данных

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

## ⚙️ Airflow DAG

```
de_portfolio_ingestion (every 6 hours)
│
├── git_pull              — обновляет код с GitHub
├── ingest_all_sources    — запускает все 7 источников
└── staging_transform     — raw.* → staging.*
```

---

## [+] Структура проекта

```
de-portfolio/
├── .github/workflows/
│   ├── ingest.yml          # manual only (Airflow заменил cron)
│   ├── transform.yml       # manual only (Airflow заменил cron)
│   └── migrate.yml         # ручные DDL миграции
├── dags/
│   └── de_portfolio_ingestion.py   # Airflow DAG
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
│       └── kafka_consumer.py
├── sql/migrations/
│   ├── 001_init_schemas.sql
│   └── 002_staging_transform.sql
└── requirements.txt
```

---

## >_ Быстрый старт

**1. Добавь секрет в GitHub**
```
Settings → Secrets → Actions → New secret
Name:  DATABASE_URL
Value: postgresql://user:pass@host/dbname?sslmode=require
```

**2. Создай схемы БД**
```
Actions → Database Migration → Run workflow → 001_init_schemas.sql
```

**3. Запусти ingestion вручную**
```
Actions → Data Ingestion → Run workflow
```

**4. Запусти трансформации**
```
Actions → Staging Transform → Run workflow
```

---

## [->] Roadmap

- [x] Multi-source ingestion (7 sources)
- [x] PostgreSQL DWH (raw / staging / mart)
- [x] Apache Kafka streaming (producer + consumer)
- [x] Apache Airflow orchestration (homelab)
- [x] Database migrations via Git
- [x] BI Dashboards (Apache Superset)
- [x] Homelab server (Ubuntu + Docker)
- [ ] Apache Spark (batch processing)
- [ ] dbt (transformations as code)
- [ ] Great Expectations (data quality)
- [ ] Grafana (pipeline monitoring)
- [ ] Cloudflare Tunnel (public access)

---

## [ @ ] Автор

**GabYer** — Data Engineer, Astana, Kazakhstan

[![GitHub](https://img.shields.io/badge/GitHub-GabYer-black?logo=github)](https://github.com/GabYer)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-gabyer-blue?logo=linkedin)](https://www.linkedin.com/in/gabyer/)
[![Email](https://img.shields.io/badge/Email-gyermekbayev@gmail.com-red?logo=gmail)](mailto:gyermekbayev@gmail.com)
