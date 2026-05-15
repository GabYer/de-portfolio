# 🇰🇿 Kazakhstan Data Engineering Portfolio


````md
   ______      __   __     __           
  / ____/___ _/ /_ / /_  __/ /__  _____ 
 / / __/ __ `/ __ `/ / / / / / _ \/ ___/
/ /_/ / /_/ / /_/ / / /_/ / /  __/ /    
\____/\__,_/\__,_/_/\__, /_/\___/_/     
                   /____/
````

> **End-to-end data pipeline** — автоматический сбор данных из 5 источников,
> PostgreSQL DWH с 3-слойной архитектурой и BI дашборды онлайн.

[![Data Ingestion](https://github.com/GabYer/de-portfolio/actions/workflows/ingest.yml/badge.svg)](https://github.com/GabYer/de-portfolio/actions/workflows/ingest.yml)
[![Staging Transform](https://github.com/GabYer/de-portfolio/actions/workflows/transform.yml/badge.svg)](https://github.com/GabYer/de-portfolio/actions/workflows/transform.yml)

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                           │
│                                                             │
│  CoinGecko API   НБК Казахстан   Open-Meteo   Tengrinews    │
│  (BTC/ETH/BNB)   (KZT курсы)     (погода)     (новости)     │
│                                                             │
│                    Event Generator                          │
│              (транзакции / клики / IoT)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │  Python (requests, BeautifulSoup, Faker)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               GitHub Actions (cron every 6h)                │
│                                                             │
│   ingest.yml → raw.*    │   transform.yml → staging.*       │
│   migrate.yml (manual)  │                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL DWH — Neon.tech                     │
│                                                             │
│  ┌─────────┐    ┌──────────┐    ┌──────────────────────┐    │
│  │  raw.*  │ →  │staging.* │ →  │       mart.*         │    │
│  │         │    │          │    │                      │    │
│  │ as-is   │    │ cleaned  │    │ daily_crypto_kzt     │    │
│  │ data    │    │ deduped  │    │ forex_trend          │    │
│  │         │    │ typed    │    │ txn_hourly           │    │
│  └─────────┘    └──────────┘    │ fraud_signals        │    │
│                                 │ news_by_category     │    │
│  meta.pipeline_runs (logs)      └──────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           Apache Superset — Railway.app                     │
│                                                             │
│   📈 Крипто в KZT    💱 Курсы валют    🛒 Транзакции       │
│   📰 Новости КЗ      🚨 Fraud Signals                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Стек технологий

| Слой | Технология | Описание |
|------|-----------|----------|
| Ingestion | Python 3.11 | requests, BeautifulSoup4, Faker |
| Database | PostgreSQL 16 (Neon.tech) | DWH: raw / staging / mart / meta |
| Orchestration | GitHub Actions | Cron каждые 6 часов, 3 workflow |
| Migrations | psql + SQL files | Версионированные DDL миграции |
| BI | Apache Superset (Railway.app) | Дашборды поверх mart.* |

---

## 📊 Источники данных

| # | Источник | Тип | Данные | Таблица |
|---|---------|-----|--------|---------|
| 1 | CoinGecko API | REST API | BTC, ETH, BNB цены в USD | `raw.crypto_prices` |
| 2 | НБК Казахстан | REST API | USD/EUR/RUB/CNY/GBP → KZT | `raw.forex_rates_nbk` |
| 3 | Open-Meteo | REST API | Погода: Астана, Алматы, Шымкент | `raw.weather_astana` |
| 4 | Faker Generator | Event Gen | Транзакции, клики, IoT датчики | `raw.events_*` |
| 5 | Tengrinews.kz | Web Scraping | Новости Казахстана | `raw.tengri_news` |

---

## 🗄️ Схема базы данных

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

## ⚙️ GitHub Actions Workflows

| Workflow | Триггер | Действие |
|----------|---------|---------|
| ingest.yml | cron `0 */6 * * *` | raw.* ← 5 источников |
| transform.yml | cron `30 */6 * * *` | staging.* ← raw.* |
| migrate.yml | только вручную | DDL из sql/migrations/ |

---

## 📁 Структура проекта

```
de-portfolio/
├── .github/workflows/
│   ├── ingest.yml
│   ├── transform.yml
│   └── migrate.yml
├── ingestion/
│   ├── db.py
│   ├── run_all.py
│   └── sources/
│       ├── crypto_api.py
│       ├── nbk_forex.py
│       ├── weather_api.py
│       ├── event_generator.py
│       └── tengri_scraper.py
├── sql/migrations/
│   ├── 001_init_schemas.sql
│   └── 002_staging_transform.sql
└── requirements.txt
```

---

## 🚀 Быстрый старт

**1. Добавь секрет в GitHub**
```
Settings → Secrets → Actions → New secret
Name:  DATABASE_URL
Value: postgresql://user:pass@host/dbname?sslmode=require
```

**2. Создай схемы**
```
Actions → Database Migration → Run workflow → 001_init_schemas.sql
```

**3. Запусти ingestion**
```
Actions → Data Ingestion → Run workflow
```

**4. Запусти трансформации**
```
Actions → Staging Transform → Run workflow
```

---

## 🗺️ Roadmap

- [x] Multi-source ingestion (5 sources)
- [x] PostgreSQL DWH (raw / staging / mart)
- [x] Automated orchestration (GitHub Actions)
- [x] Database migrations via Git
- [x] BI Dashboards (Apache Superset)
- [ ] Apache Kafka + Flink (real-time streaming)
- [ ] Apache Spark (batch processing)
- [ ] Apache Airflow (orchestration)
- [ ] dbt (transformations as code)
- [ ] Great Expectations (data quality)
- [ ] Grafana (pipeline monitoring)

---

## 👤 Автор

**GabYer** — Data Engineer, Astana, Kazakhstan

[![GitHub](https://img.shields.io/badge/GitHub-GabYer-black?logo=github)](https://github.com/GabYer)
