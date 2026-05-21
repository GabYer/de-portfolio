{{ config(materialized='view') }}

SELECT
    DATE_TRUNC('hour', event_ts)                                AS hour,
    city,
    channel,
    category,
    COUNT(*)                                                    AS txn_count,
    ROUND(SUM(amount_kzt)::NUMERIC, 0)                         AS total_kzt,
    ROUND(AVG(amount_kzt)::NUMERIC, 0)                         AS avg_kzt,
    SUM(CASE WHEN status = 'declined'  THEN 1 ELSE 0 END)     AS declined_count,
    SUM(CASE WHEN is_fraud_flag = TRUE THEN 1 ELSE 0 END)     AS fraud_count
FROM {{ ref('stg_transactions') }}
GROUP BY DATE_TRUNC('hour', event_ts), city, channel, category
ORDER BY hour DESC
