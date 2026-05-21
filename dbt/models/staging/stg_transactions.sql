{{ config(materialized='table') }}

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
FROM {{ source('raw', 'events_transactions') }}
WHERE amount_kzt > 0
  AND user_id IS NOT NULL
  AND event_ts >= NOW() - INTERVAL '30 days'
ORDER BY event_id, loaded_at DESC
