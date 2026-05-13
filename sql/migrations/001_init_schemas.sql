-- ============================================================
-- Senior DE Portfolio — Neon.tech PostgreSQL DDL
-- Запуск: psql $DATABASE_URL -f 01_create_schemas.sql
-- ============================================================

-- Схемы
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS meta;

-- ============================================================
-- META — служебные таблицы мониторинга пайплайна
-- ============================================================

CREATE TABLE IF NOT EXISTS meta.pipeline_runs (
                                                  id              BIGSERIAL PRIMARY KEY,
                                                  pipeline_name   TEXT        NOT NULL,
                                                  source          TEXT        NOT NULL,
                                                  status          TEXT        NOT NULL CHECK (status IN ('running','success','failed','skipped')),
    rows_extracted  INTEGER     DEFAULT 0,
    rows_loaded     INTEGER     DEFAULT 0,
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at     TIMESTAMPTZ
    );

CREATE TABLE IF NOT EXISTS meta.load_watermarks (
                                                    source          TEXT        PRIMARY KEY,
                                                    last_loaded_at  TIMESTAMPTZ NOT NULL,
                                                    last_value      TEXT,
                                                    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS meta.source_health (
                                                  id              BIGSERIAL PRIMARY KEY,
                                                  source          TEXT        NOT NULL,
                                                  checked_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_available    BOOLEAN     NOT NULL,
    response_ms     INTEGER,
    http_status     INTEGER,
    error_msg       TEXT
    );

-- ============================================================
-- RAW — 1. REST API: Крипто и финансы
-- ============================================================

CREATE TABLE IF NOT EXISTS raw.crypto_prices (
                                                 id                    BIGSERIAL PRIMARY KEY,
                                                 loaded_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    coin_id               TEXT        NOT NULL,
    coin_name             TEXT,
    symbol                TEXT,
    current_price_usd     NUMERIC(24,8),
    market_cap_usd        NUMERIC(30,2),
    total_volume_usd      NUMERIC(30,2),
    price_change_24h      NUMERIC(14,4),
    price_change_pct_24h  NUMERIC(10,4),
    circulating_supply    NUMERIC(30,4),
    ath_usd               NUMERIC(24,8),
    ath_date              TIMESTAMPTZ,
    source_snapshot_at    TIMESTAMPTZ,
    _raw_json             JSONB
    );
CREATE INDEX IF NOT EXISTS idx_crypto_coin_loaded
    ON raw.crypto_prices (coin_id, loaded_at DESC);

CREATE TABLE IF NOT EXISTS raw.forex_rates_nbk (
                                                   id              BIGSERIAL PRIMARY KEY,
                                                   loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rate_date       DATE        NOT NULL,
    currency_code   TEXT        NOT NULL,
    currency_name   TEXT,
    units           INTEGER,
    rate_kzt        NUMERIC(16,4),
    change_kzt      NUMERIC(14,4),
    source_url      TEXT
    );
CREATE UNIQUE INDEX IF NOT EXISTS idx_forex_nbk_date_code
    ON raw.forex_rates_nbk (rate_date, currency_code);

CREATE TABLE IF NOT EXISTS raw.weather_astana (
                                                  id              BIGSERIAL PRIMARY KEY,
                                                  loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    observed_at     TIMESTAMPTZ NOT NULL,
    city            TEXT        NOT NULL DEFAULT 'Астана',
    latitude        NUMERIC(8,4),
    longitude       NUMERIC(8,4),
    temp_celsius    NUMERIC(5,2),
    humidity_pct    NUMERIC(5,2),
    wind_speed_ms   NUMERIC(6,2),
    precipitation   NUMERIC(8,4),
    weather_code    INTEGER,
    _raw_json       JSONB
    );
CREATE INDEX IF NOT EXISTS idx_weather_observed
    ON raw.weather_astana (observed_at DESC);

-- ============================================================
-- RAW — 2. CSV/API: Открытые данные Казахстана
-- ============================================================

CREATE TABLE IF NOT EXISTS raw.kz_goszakup (
                                               id                  BIGSERIAL PRIMARY KEY,
                                               loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tender_id           TEXT,
    lot_number          TEXT,
    customer_bin        TEXT,
    customer_name       TEXT,
    supplier_bin        TEXT,
    supplier_name       TEXT,
    contract_sum_kzt    NUMERIC(24,2),
    subject             TEXT,
    status              TEXT,
    published_at        DATE,
    signed_at           DATE,
    region_code         TEXT,
    trd_buy_type_code   TEXT,
    _raw_json           JSONB
    );
CREATE INDEX IF NOT EXISTS idx_goszakup_loaded
    ON raw.kz_goszakup (loaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_goszakup_tender
    ON raw.kz_goszakup (tender_id);

CREATE TABLE IF NOT EXISTS raw.kz_stat_regions (
                                                   id              BIGSERIAL PRIMARY KEY,
                                                   loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    period_year     INTEGER,
    period_month    INTEGER,
    region_code     TEXT,
    region_name_ru  TEXT,
    region_name_kk  TEXT,
    indicator_code  TEXT,
    indicator_name  TEXT,
    value           NUMERIC(20,4),
    unit            TEXT,
    _raw_json       JSONB
    );

CREATE TABLE IF NOT EXISTS raw.kz_companies (
                                                id              BIGSERIAL PRIMARY KEY,
                                                loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    bin             TEXT,
    name_ru         TEXT,
    name_kk         TEXT,
    oked_code       TEXT,
    oked_name       TEXT,
    region_code     TEXT,
    registration_date DATE,
    status          TEXT,
    krp_code        TEXT,
    _raw_json       JSONB
    );
CREATE INDEX IF NOT EXISTS idx_companies_bin
    ON raw.kz_companies (bin);

-- ============================================================
-- RAW — 3. Web Scraping: Kolesa.kz
-- ============================================================

-- CREATE TABLE IF NOT EXISTS raw.kolesa_listings (
--                                                    id              BIGSERIAL PRIMARY KEY,
--                                                    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
--                                                    scraped_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
--                                                    listing_id      TEXT,
--                                                    url             TEXT,
--                                                    brand           TEXT,
--                                                    model           TEXT,
--                                                    year            INTEGER,
--                                                    mileage_km      INTEGER,
--                                                    price_kzt       NUMERIC(16,2),
--                                                    price_usd       NUMERIC(12,2),
--                                                    city            TEXT,
--                                                    transmission    TEXT,
--                                                    fuel_type       TEXT,
--                                                    body_type       TEXT,
--                                                    color           TEXT,
--                                                    description     TEXT,
--                                                    seller_type     TEXT,
--                                                    is_active       BOOLEAN     DEFAULT TRUE,
--                                                    _raw_html       TEXT
-- );
-- CREATE INDEX IF NOT EXISTS idx_kolesa_listing_id
--     ON raw.kolesa_listings (listing_id);
-- CREATE INDEX IF NOT EXISTS idx_kolesa_scraped
--     ON raw.kolesa_listings (scraped_at DESC);

-- ============================================================
-- RAW — 3. Web Scraping: tengri_news.kz
-- ============================================================

CREATE TABLE IF NOT EXISTS raw.tengri_news (
                                               id            BIGSERIAL PRIMARY KEY,
                                               loaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    url           TEXT        NOT NULL,
    title         TEXT        NOT NULL,
    category      TEXT,
    description   TEXT,
    published_at  TIMESTAMPTZ,
    scraped_at    TIMESTAMPTZ NOT NULL,
    UNIQUE(url)
    );

CREATE TABLE IF NOT EXISTS raw.scrape_runs (
                                               id              BIGSERIAL PRIMARY KEY,
                                               source          TEXT        NOT NULL,
                                               started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at     TIMESTAMPTZ,
    pages_scraped   INTEGER     DEFAULT 0,
    rows_scraped    INTEGER     DEFAULT 0,
    status          TEXT        CHECK (status IN ('running','success','failed')),
    error_msg       TEXT
    );

-- ============================================================
-- RAW — 4. Event Generator: синтетические события
-- ============================================================

CREATE TABLE IF NOT EXISTS raw.events_transactions (
                                                       id              BIGSERIAL PRIMARY KEY,
                                                       loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_id        UUID        NOT NULL DEFAULT gen_random_uuid(),
    event_ts        TIMESTAMPTZ NOT NULL,
    user_id         TEXT        NOT NULL,
    session_id      TEXT,
    amount_kzt      NUMERIC(14,2) NOT NULL,
    currency        TEXT        NOT NULL DEFAULT 'KZT',
    merchant_id     TEXT,
    merchant_name   TEXT,
    category        TEXT,
    city            TEXT,
    channel         TEXT        CHECK (channel IN ('mobile','web','pos','atm')),
    status          TEXT        CHECK (status IN ('approved','declined','pending')),
    is_fraud_flag   BOOLEAN     DEFAULT FALSE,
    _raw_json       JSONB
    );
CREATE INDEX IF NOT EXISTS idx_txn_event_ts
    ON raw.events_transactions (event_ts DESC);
CREATE INDEX IF NOT EXISTS idx_txn_user
    ON raw.events_transactions (user_id);

CREATE TABLE IF NOT EXISTS raw.events_clickstream (
                                                      id              BIGSERIAL PRIMARY KEY,
                                                      loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_id        UUID        NOT NULL DEFAULT gen_random_uuid(),
    event_ts        TIMESTAMPTZ NOT NULL,
    session_id      TEXT        NOT NULL,
    user_id         TEXT,
    event_type      TEXT        CHECK (event_type IN ('page_view','click','search','add_to_cart','purchase')),
    page_url        TEXT,
    referrer        TEXT,
    device_type     TEXT        CHECK (device_type IN ('mobile','tablet','desktop')),
    os              TEXT,
    country         TEXT        DEFAULT 'KZ',
    city            TEXT,
    duration_sec    INTEGER,
    _raw_json       JSONB
    );
CREATE INDEX IF NOT EXISTS idx_click_event_ts
    ON raw.events_clickstream (event_ts DESC);

CREATE TABLE IF NOT EXISTS raw.events_iot_sensors (
                                                      id              BIGSERIAL PRIMARY KEY,
                                                      loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_id        UUID        NOT NULL DEFAULT gen_random_uuid(),
    event_ts        TIMESTAMPTZ NOT NULL,
    sensor_id       TEXT        NOT NULL,
    sensor_type     TEXT        CHECK (sensor_type IN ('temperature','humidity','pressure','air_quality')),
    location_city   TEXT,
    latitude        NUMERIC(8,4),
    longitude       NUMERIC(8,4),
    value           NUMERIC(10,4),
    unit            TEXT,
    is_anomaly      BOOLEAN     DEFAULT FALSE,
    battery_pct     INTEGER,
    _raw_json       JSONB
    );
CREATE INDEX IF NOT EXISTS idx_iot_sensor_ts
    ON raw.events_iot_sensors (sensor_id, event_ts DESC);

-- ============================================================
-- STAGING — очищенные данные с типизацией
-- ============================================================

CREATE TABLE IF NOT EXISTS staging.crypto_prices AS
SELECT
    coin_id, coin_name, UPPER(symbol) AS symbol,
    current_price_usd, market_cap_usd, total_volume_usd,
    price_change_24h, price_change_pct_24h, circulating_supply,
    ath_usd, ath_date, source_snapshot_at,
    DATE_TRUNC('hour', loaded_at) AS loaded_hour,
    loaded_at
FROM raw.crypto_prices WHERE 1=0;

CREATE TABLE IF NOT EXISTS staging.forex_rates AS
SELECT rate_date, currency_code, currency_name, units, rate_kzt, change_kzt, loaded_at
FROM raw.forex_rates_nbk WHERE 1=0;

-- CREATE TABLE IF NOT EXISTS staging.car_listings AS
-- SELECT
--     listing_id, brand, model, year, mileage_km,
--     price_kzt, price_usd, city, transmission,
--     fuel_type, body_type, color, seller_type,
--     scraped_at, is_active
-- FROM raw.kolesa_listings WHERE 1=0;

CREATE TABLE IF NOT EXISTS staging.transactions AS
SELECT
    event_id, event_ts, user_id, session_id,
    amount_kzt, merchant_name, category,
    city, channel, status, is_fraud_flag, loaded_at
FROM raw.events_transactions WHERE 1=0;

-- ============================================================
-- MART — аналитические вьюхи для Power BI
-- ============================================================

CREATE OR REPLACE VIEW mart.daily_crypto_kzt AS
SELECT
    DATE(s.source_snapshot_at)              AS trade_date,
    s.coin_id,
    s.coin_name,
    s.symbol,
    ROUND(AVG(s.current_price_usd)::NUMERIC, 2)  AS avg_price_usd,
    ROUND(MIN(s.current_price_usd)::NUMERIC, 2)  AS low_usd,
    ROUND(MAX(s.current_price_usd)::NUMERIC, 2)  AS high_usd,
    ROUND((AVG(s.current_price_usd) * AVG(f.rate_kzt / NULLIF(f.units,0)))::NUMERIC, 0) AS avg_price_kzt,
    ROUND(AVG(s.price_change_pct_24h)::NUMERIC, 3) AS avg_change_pct,
    MAX(s.market_cap_usd)                   AS market_cap_usd,
    MAX(s.total_volume_usd)                 AS volume_usd
FROM staging.crypto_prices s
    LEFT JOIN staging.forex_rates f
ON f.rate_date = DATE(s.source_snapshot_at)
    AND f.currency_code = 'USD'
GROUP BY DATE(s.source_snapshot_at), s.coin_id, s.coin_name, s.symbol
ORDER BY trade_date DESC, s.coin_id;

CREATE OR REPLACE VIEW mart.forex_trend AS
SELECT
    rate_date,
    currency_code,
    currency_name,
    ROUND((rate_kzt / NULLIF(units,0))::NUMERIC, 4) AS rate_per_unit,
    ROUND((rate_kzt / NULLIF(units,0) - LAG(rate_kzt / NULLIF(units,0)) OVER (
        PARTITION BY currency_code ORDER BY rate_date
        ))::NUMERIC, 4) AS day_change,
    loaded_at
FROM staging.forex_rates
ORDER BY rate_date DESC, currency_code;

CREATE OR REPLACE VIEW mart.cars_by_brand AS
SELECT
    brand,
    model,
    city,
    COUNT(*)                                AS listings_count,
    ROUND(AVG(price_kzt)::NUMERIC, 0)      AS avg_price_kzt,
    ROUND(MIN(price_kzt)::NUMERIC, 0)      AS min_price_kzt,
    ROUND(MAX(price_kzt)::NUMERIC, 0)      AS max_price_kzt,
    ROUND(AVG(mileage_km)::NUMERIC, 0)     AS avg_mileage_km,
    ROUND(AVG(year)::NUMERIC, 1)           AS avg_year,
    DATE(MAX(scraped_at))                   AS last_seen
FROM staging.car_listings
WHERE is_active = TRUE AND price_kzt > 0
GROUP BY brand, model, city
ORDER BY listings_count DESC;

CREATE OR REPLACE VIEW mart.txn_hourly AS
SELECT
    DATE_TRUNC('hour', event_ts)            AS hour,
    city,
    channel,
    category,
    COUNT(*)                                AS txn_count,
    ROUND(SUM(amount_kzt)::NUMERIC, 0)     AS total_kzt,
    ROUND(AVG(amount_kzt)::NUMERIC, 0)     AS avg_kzt,
    SUM(CASE WHEN status='declined' THEN 1 ELSE 0 END) AS declined_count,
    SUM(CASE WHEN is_fraud_flag THEN 1 ELSE 0 END)     AS fraud_count
FROM staging.transactions
GROUP BY DATE_TRUNC('hour', event_ts), city, channel, category
ORDER BY hour DESC;

CREATE OR REPLACE VIEW mart.fraud_signals AS
SELECT
    DATE(event_ts)  AS txn_date,
    user_id,
    COUNT(*)        AS total_txn,
    SUM(amount_kzt) AS total_amount,
    SUM(CASE WHEN is_fraud_flag THEN 1 ELSE 0 END)  AS fraud_count,
    ROUND(100.0 * SUM(CASE WHEN is_fraud_flag THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_pct,
    MAX(event_ts)   AS last_txn_at
FROM staging.transactions
GROUP BY DATE(event_ts), user_id
HAVING SUM(CASE WHEN is_fraud_flag THEN 1 ELSE 0 END) > 0
ORDER BY fraud_count DESC;