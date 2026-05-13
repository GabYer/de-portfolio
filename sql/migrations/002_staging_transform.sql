-- ============================================================
-- Migration: 002_staging_transform.sql
-- raw.* → staging.*  (очистка, дедупликация, типизация)
-- ============================================================

-- ============================================================
-- staging.crypto_prices
-- Дедупликация: одна запись на монету в час
-- ============================================================
TRUNCATE staging.crypto_prices;

INSERT INTO staging.crypto_prices (
    coin_id, coin_name, symbol,
    current_price_usd, market_cap_usd, total_volume_usd,
    price_change_24h, price_change_pct_24h,
    circulating_supply, ath_usd, ath_date,
    source_snapshot_at, loaded_hour, loaded_at
)
SELECT DISTINCT ON (coin_id, DATE_TRUNC('hour', loaded_at))
    coin_id,
    coin_name,
    UPPER(TRIM(symbol))             AS symbol,
    current_price_usd,
    market_cap_usd,
    total_volume_usd,
    price_change_24h,
    price_change_pct_24h,
    circulating_supply,
    ath_usd,
    ath_date,
    source_snapshot_at,
    DATE_TRUNC('hour', loaded_at)   AS loaded_hour,
    loaded_at
FROM raw.crypto_prices
WHERE current_price_usd > 0
  AND coin_id IS NOT NULL
ORDER BY coin_id, DATE_TRUNC('hour', loaded_at), loaded_at DESC;

-- ============================================================
-- staging.forex_rates
-- Дедупликация: одна запись на дату + валюту
-- ============================================================
TRUNCATE staging.forex_rates;

INSERT INTO staging.forex_rates (
    rate_date, currency_code, currency_name,
    units, rate_kzt, change_kzt, loaded_at
)
SELECT DISTINCT ON (rate_date, currency_code)
    rate_date,
    UPPER(TRIM(currency_code))      AS currency_code,
    INITCAP(TRIM(currency_name))    AS currency_name,
    COALESCE(units, 1)              AS units,
    rate_kzt,
    change_kzt,
    loaded_at
FROM raw.forex_rates_nbk
WHERE rate_kzt > 0
  AND currency_code IS NOT NULL
ORDER BY rate_date, currency_code, loaded_at DESC;

-- ============================================================
-- staging.transactions
-- Дедупликация по event_id, фильтр мусора
-- ============================================================
TRUNCATE staging.transactions;

INSERT INTO staging.transactions (
    event_id, event_ts, user_id, session_id,
    amount_kzt, merchant_name, category,
    city, channel, status, is_fraud_flag, loaded_at
)
SELECT DISTINCT ON (event_id)
    event_id,
    event_ts,
    TRIM(user_id)                   AS user_id,
    session_id,
    ROUND(amount_kzt, 2)            AS amount_kzt,
    INITCAP(TRIM(merchant_name))    AS merchant_name,
    LOWER(TRIM(category))           AS category,
    INITCAP(TRIM(city))             AS city,
    LOWER(TRIM(channel))            AS channel,
    LOWER(TRIM(status))             AS status,
    COALESCE(is_fraud_flag, FALSE)  AS is_fraud_flag,
    loaded_at
FROM raw.events_transactions
WHERE amount_kzt > 0
  AND user_id IS NOT NULL
  AND event_ts >= NOW() - INTERVAL '30 days'
ORDER BY event_id, loaded_at DESC;

-- ============================================================
-- staging.news
-- Дедупликация по url, фильтр коротких заголовков
-- ============================================================
TRUNCATE staging.news;

INSERT INTO staging.news (
    url, title, category, description, published_at, scraped_at
)
SELECT DISTINCT ON (url)
    url,
    TRIM(title)                     AS title,
    INITCAP(TRIM(category))         AS category,
    description,
    published_at,
    scraped_at
FROM raw.tengri_news
WHERE title IS NOT NULL
  AND LENGTH(TRIM(title)) > 10
  AND published_at >= NOW() - INTERVAL '7 days'
ORDER BY url, scraped_at DESC;

-- ============================================================
-- Лог трансформации
-- ============================================================
INSERT INTO meta.pipeline_runs
(pipeline_name, source, status, rows_loaded, started_at, finished_at)
VALUES
    ('staging_transform', 'sql', 'success',
     (SELECT COUNT(*) FROM staging.crypto_prices) +
     (SELECT COUNT(*) FROM staging.forex_rates) +
     (SELECT COUNT(*) FROM staging.transactions) +
     (SELECT COUNT(*) FROM staging.news),
     NOW(), NOW());