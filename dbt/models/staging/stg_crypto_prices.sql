{{ config(materialized='table') }}

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
FROM {{ source('raw', 'crypto_prices') }}
WHERE current_price_usd > 0
  AND coin_id IS NOT NULL
ORDER BY coin_id, DATE_TRUNC('hour', loaded_at), loaded_at DESC
