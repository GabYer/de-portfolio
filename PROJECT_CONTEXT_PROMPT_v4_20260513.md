# 🚀 Senior Data Engineer Portfolio — Project Context Prompt
## Version: 4.0 | Date: 2026-05-13 | Stage: Core Pipeline Complete ✅

---

## WHO I AM
- Data Engineer from **Kazakhstan (Astana)**
- **Python beginner** — explain every step simply, no terminal commands
- Everything runs **online only** — GitHub, Neon, Railway
- Uses **IntelliJ IDEA** for editing — give only file path + full code
- GitHub user: **GabYer**, repo: **de-portfolio**

---

## GOAL
Full end-to-end Senior Data Engineer portfolio demonstrating:
- Multi-source ingestion (REST API, Web Scraping, Event Generator)
- PostgreSQL DWH (raw → staging → mart)
- Automated orchestration via GitHub Actions
- BI dashboards (Apache Superset)
- Streaming: Kafka + Flink (next)
- Batch: Apache Spark (next)
- Orchestration: Apache Airflow (next)
- Transformations: dbt (next)
- Data Quality: Great Expectations (next)

---

## INFRASTRUCTURE — ALL ONLINE ✅

| Service | Tool | Status |
|---------|------|--------|
| Code + CI/CD | GitHub (GabYer/de-portfolio) | ✅ |
| Scheduler | GitHub Actions (cron every 6h) | ✅ |
| Database DWH | Neon.tech PostgreSQL 16 | ✅ |
| BI Dashboard | Apache Superset on Railway.app | ✅ |

---

## NEON CONNECTION

```
Host:     ep-empty-base-alumbcid-pooler.c-3.eu-central-1.aws.neon.tech
Port:     5432
Database: neondb
User:     neondb_owner
SSL:      require
DATABASE_URL: postgresql://neondb_owner:PASSWORD@ep-empty-base-alumbcid-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

---

## GITHUB REPOSITORY STRUCTURE

```
de-portfolio/
├── requirements.txt                         ✅
├── README.md                                ⬜ нужно создать
├── .github/
│   └── workflows/
│       ├── ingest.yml                       ✅ cron 0 */6 * * *
│       ├── transform.yml                    ✅ cron 30 */6 * * *
│       └── migrate.yml                      ✅ manual only
├── ingestion/
│   ├── db.py                                ✅
│   ├── run_all.py                           ✅
│   └── sources/
│       ├── __init__.py                      ✅
│       ├── crypto_api.py                    ✅ CoinGecko
│       ├── nbk_forex.py                     ✅ НБК курсы
│       ├── weather_api.py                   ✅ Open-Meteo
│       ├── event_generator.py               ✅ Faker
│       └── tengri_scraper.py                ✅ Tengrinews.kz
└── sql/
    └── migrations/
        ├── 001_init_schemas.sql             ✅ DDL всех таблиц
        └── 002_staging_transform.sql        ✅ raw → staging
```

---

## DATA SOURCES — ALL WORKING ✅

| # | Source | Type | File | Table | Rows/run |
|---|--------|------|------|-------|----------|
| 1 | CoinGecko | REST API | crypto_api.py | raw.crypto_prices | 3 |
| 2 | НБК Казахстан | REST API | nbk_forex.py | raw.forex_rates_nbk | 5 |
| 3 | Open-Meteo | REST API | weather_api.py | raw.weather_astana | 3 |
| 4 | Faker | Event Generator | event_generator.py | raw.events_* | 160 |
| 5 | Tengrinews.kz | Web Scraping | tengri_scraper.py | raw.tengri_news | 30 |

---

## DATABASE — Neon PostgreSQL ✅

### All schemas created and populated:
```
raw.*      — данные как есть из источников
staging.*  — очищенные, дедуплицированные  
mart.*     — вьюхи для BI
meta.*     — логи пайплайна
```

### Staging (populated every 6h+30min):
```
staging.crypto_prices   ✅
staging.forex_rates     ✅
staging.transactions    ✅
staging.news            ✅
```

### Mart views (always fresh):
```
mart.daily_crypto_kzt   ✅ крипто в KZT по дням
mart.forex_trend        ✅ динамика курсов валют
mart.txn_hourly         ✅ транзакции по часам
mart.fraud_signals      ✅ подозрительные транзакции
mart.news_by_category   ✅ новости по категориям
```

---

## GITHUB ACTIONS — 3 WORKFLOWS ✅

| Workflow | Триггер | Что делает |
|----------|---------|-----------|
| ingest.yml | каждые 6ч + вручную | raw.* ← 5 источников |
| transform.yml | каждые 6ч+30мин + вручную | staging.* ← raw.* |
| migrate.yml | только вручную | DDL миграции из sql/migrations/ |

### Pipeline schedule:
```
00:00 / 06:00 / 12:00 / 18:00  →  ingest.yml
00:30 / 06:30 / 12:30 / 18:30  →  transform.yml
```

---

## BI — APACHE SUPERSET ✅

**URL:** https://superset-production-0c30.up.railway.app
**Platform:** Railway.app
**Connected to:** Neon PostgreSQL (mart.* schema)

### Dashboards built:
- ✅ Крипто цены в KZT (Line Chart)
- ✅ Изменение цены 24ч % (Bar Chart)
- ✅ Курсы валют к KZT (Line Chart)
- ✅ Транзакции по городам (Bar Chart)
- ✅ Каналы транзакций (Pie Chart)
- ✅ Dashboard: "DE Portfolio — Kazakhstan Data"

---

## NEXT STEPS (priority order)

### 1. ⬜ README.md — ПРИОРИТЕТ
Профессиональный README с архитектурной схемой для GitHub.
Это первое что видит рекрутер. Важнее всего остального сейчас.

### 2. ⬜ Docker Compose — локальный стриминг стек
```
Kafka + Zookeeper   — message broker
Apache Flink        — stream processing
Apache Airflow      — orchestration
Apache Spark        — batch processing
```

### 3. ⬜ dbt — трансформации
Заменить 002_staging_transform.sql на dbt models.
Добавить tests, documentation, lineage.

### 4. ⬜ Great Expectations — data quality
Проверки качества данных после ingestion.

### 5. ⬜ data.egov.kz — ещё один источник
Госзакупки и реестр компаний Казахстана.

### 6. ⬜ Grafana Cloud — мониторинг пайплайна
Метрики из meta.pipeline_runs в Grafana дашборд.

---

## RULES FOR ANY AI ASSISTANT

1. **Python beginner** — объясняй каждый шаг просто
2. **Всё онлайн** — никаких локальных команд
3. **IntelliJ IDEA** — давай только путь файла и полный код
4. **Полный код всегда** — никогда не показывай частичный код
5. **Один файл за раз** — жди подтверждения
6. **Никогда не хардкодить пароли** — только GitHub Secrets

---

## HOW TO CONTINUE

Вставь этот файл в новый чат и напиши:

> "Это контекст моего Senior DE портфолио.
> Core pipeline полностью работает: 5 источников → Neon DWH → Superset дашборды.
> Следующий шаг: [что хочешь сделать]"

### Готовые фразы:
- "Напиши профессиональный README.md для GitHub репо"
- "Настрой Docker Compose с Kafka + Flink + Airflow + Spark"
- "Добавь dbt вместо SQL трансформаций"
- "Добавь Great Expectations для проверки качества данных"
- "Добавь источник data.egov.kz в пайплайн"
- "Настрой Grafana Cloud для мониторинга пайплайна"
