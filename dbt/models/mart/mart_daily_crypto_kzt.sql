{{ config(materialized='view') }}

SELECT
    DATE(s.source_snapshot_at)                                                          AS trade_date,
    s.coin_id,
    s.coin_name,
    s.symbol,
    ROUND(AVG(s.current_price_usd)::NUMERIC, 2)                                        AS avg_price_usd,
    ROUND(MIN(s.current_price_usd)::NUMERIC, 2)                                        AS low_usd,
    ROUND(MAX(s.current_price_usd)::NUMERIC, 2)                                        AS high_usd,
    ROUND((AVG(s.current_price_usd) * AVG(f.rate_kzt / NULLIF(f.units,0)))::NUMERIC, 0) AS avg_price_kzt,
    ROUND(AVG(s.price_change_pct_24h)::NUMERIC, 3)                                    AS avg_change_pct,
    MAX(s.market_cap_usd)                                                               AS market_cap_usd,
    MAX(s.total_volume_usd)                                                             AS volume_usd
FROM {{ ref('stg_crypto_prices') }} s
LEFT JOIN {{ ref('stg_forex_rates') }} f
    ON f.rate_date = DATE(s.source_snapshot_at)
    AND f.currency_code = 'USD'
GROUP BY DATE(s.source_snapshot_at), s.coin_id, s.coin_name, s.symbol
ORDER BY trade_date DESC, s.coin_id
