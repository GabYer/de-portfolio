# 🚀 Senior Data Engineer Portfolio — Project Context Prompt
## Version: 3.0 | Date: 2026-05-13 | Stage: Staging Complete → BI Setup

---

## WHO I AM
- Data Engineer from **Kazakhstan (Astana)**
- **Python beginner** — explain every step simply, no terminal commands
- Everything runs **online only** — GitHub, Neon, Railway, no local execution
- Uses **IntelliJ IDEA** for editing code — just give file path and code, no "click pencil" instructions
- GitHub user: **GabYer**, repo: **de-portfolio**

---

## GOAL
Full end-to-end Senior Data Engineer portfolio:
- Multi-source ingestion → PostgreSQL DWH (raw/staging/mart) → BI dashboards
- Demonstrates: ETL, DWH design, orchestration, data quality, streaming (future)

---

## INFRASTRUCTURE

| Service | Tool | URL | Cost |
|---------|------|-----|------|
| Code + CI/CD | GitHub | github.com/GabYer/de-portfolio | FREE |
| Scheduler | GitHub Actions | cron every 6h | FREE |
| Database | Neon.tech PostgreSQL 16 | neon.tech | FREE 3GB |
| BI Dashboard | Apache Superset | Railway.app | FREE |

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
│       ├── crypto_api.py                    ✅ WORKING
│       ├── nbk_forex.py                     ✅ WORKING
│       ├── weather_api.py                   ✅ WORKING
│       ├── event_generator.py               ✅ WORKING
│       └── tengri_scraper.py                ✅ WORKING (30 news/run)
└── sql/
    └── migrations/
        ├── 001_init_schemas.sql             ✅ all DDL
        └── 002_staging_transform.sql        ✅ raw → staging
```

---

## DATA SOURCES — ALL WORKING ✅

| Source | File | Table | Rows/run |
|--------|------|-------|----------|
| CoinGecko API | crypto_api.py | raw.crypto_prices | 3 |
| НБК курсы | nbk_forex.py | raw.forex_rates_nbk | 5 |
| Open-Meteo погода | weather_api.py | raw.weather_astana | 3 |
| Faker events | event_generator.py | raw.events_* | 160 |
| Tengrinews.kz | tengri_scraper.py | raw.tengri_news | 30 |

---

## DATABASE ARCHITECTURE

### Schemas
```
raw.*      — данные как есть из источников
staging.*  — очищенные, дедуплицированные
mart.*     — вьюхи для BI
meta.*     — логи пайплайна
```

### Staging tables (populated ✅)
```
staging.crypto_prices   — 6 строк
staging.forex_rates     — 5 строк
staging.transactions    — 150 строк
staging.news            — 30 строк
```

### Mart views (ready for BI ✅)
```
mart.daily_crypto_kzt   — крипто в KZT по дням
mart.forex_trend        — динамика курсов валют
mart.txn_hourly         — транзакции по часам
mart.fraud_signals      — подозрительные транзакции
mart.news_by_category   — новости по категориям
```

### Meta
```
meta.pipeline_runs      — лог каждого запуска
meta.load_watermarks    — watermark по источнику
meta.source_health      — здоровье источников
```

---

## GITHUB ACTIONS — 3 WORKFLOWS

### ingest.yml — каждые 6 часов
```
raw.crypto_prices    +3 строки
raw.forex_rates_nbk  +5 строк
raw.weather_astana   +3 строки
raw.events_*         +160 строк
raw.tengri_news      +30 строк (UNIQUE url — дубли игнорируются)
```

### transform.yml — каждые 6ч + 30 мин
```
TRUNCATE + INSERT staging.* из raw.*
Дедупликация, UPPER/TRIM/INITCAP, фильтры качества
Логирует результат в meta.pipeline_runs
```

### migrate.yml — только вручную
```
Запускает любой файл из sql/migrations/
Поле ввода: имя файла (например 001_init_schemas.sql)
```

---

## BI — APACHE SUPERSET (IN PROGRESS)

**Platform:** Railway.app
**Status:** 🔄 Setting up

### Connection string for Superset → Neon:
```
postgresql://neondb_owner:PASSWORD@ep-empty-base-alumbcid-pooler.c-3.eu-central-1.aws.neon.tech/neondb
```

### Dashboards to build:
1. **Crypto Dashboard** — BTC/ETH/BNB цены в KZT, динамика, изменение за 24ч
2. **Forex Dashboard** — курсы USD/EUR/RUB/CNY/GBP к тенге, тренды
3. **Transactions Dashboard** — объёмы по городам/каналам, fraud signals
4. **Kazakhstan News** — топ категории, активность по времени

---

## PIPELINE SCHEDULE

```
00:00  ingest.yml    → raw.*
00:30  transform.yml → staging.* + mart.*
06:00  ingest.yml    → raw.*
06:30  transform.yml → staging.* + mart.*
12:00  ingest.yml    → raw.*
12:30  transform.yml → staging.* + mart.*
18:00  ingest.yml    → raw.*
18:30  transform.yml → staging.* + mart.*
```

---

## KNOWN ISSUES

| Issue | Status |
|-------|--------|
| Tengri /news/ и /kazakhstan_news/ иногда 0 | Minor — Экономика стабильно работает |
| Staging DROP+TRUNCATE при каждом запуске | OK для портфолио |
| Power BI не подходит — нет онлайн подключения к PostgreSQL | Заменён на Superset |

---

## NEXT STEPS (in order)

1. 🔄 **Superset на Railway** — подключить Neon, создать дашборды
2. ⬜ **data.egov.kz** — добавить госзакупки Казахстана
3. ⬜ **dbt models** — заменить SQL трансформации на dbt
4. ⬜ **Great Expectations** — data quality checks
5. ⬜ **Docker Compose** — Kafka + Flink + Airflow локально
6. ⬜ **README.md** — архитектурная диаграмма для GitHub

---

## RULES FOR ANY AI ASSISTANT

1. **Python beginner** — объясняй каждый шаг просто
2. **Всё онлайн** — никаких локальных команд
3. **IntelliJ IDEA** — давай только путь файла и код, без инструкций "нажми карандаш"
4. **Полный код всегда** — никогда не показывай частичный код
5. **Один файл за раз** — жди подтверждения перед следующим
6. **Никогда не хардкодить пароли** — только через GitHub Secrets или env

---

## HOW TO CONTINUE

Вставь этот файл в новый чат и напиши:

> "Это контекст моего Senior DE портфолио проекта.
> Пайплайн работает: 5 источников → Neon PostgreSQL (raw/staging/mart) → каждые 6 часов автоматически.
> Следующий шаг: [что хочешь сделать]"

### Готовые фразы:
- "Помоги настроить Apache Superset на Railway.app и подключить к Neon"
- "Создай дашборд в Superset для крипто данных"
- "Добавь источник data.egov.kz в пайплайн"
- "Настрой dbt вместо SQL трансформаций"
- "Добавь Great Expectations для проверки качества данных"
- "Настрой Docker Compose с Kafka + Flink + Airflow"
- "Напиши README.md с архитектурной диаграммой"
