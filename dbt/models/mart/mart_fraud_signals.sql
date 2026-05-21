{{ config(materialized='view') }}

SELECT
    DATE(event_ts)                                              AS txn_date,
    user_id,
    COUNT(*)                                                    AS total_txn,
    SUM(amount_kzt)                                             AS total_amount,
    SUM(CASE WHEN is_fraud_flag = TRUE THEN 1 ELSE 0 END)     AS fraud_count,
    ROUND(100.0 * SUM(CASE WHEN is_fraud_flag = TRUE THEN 1 ELSE 0 END)
        / COUNT(*), 2)                                          AS fraud_pct,
    MAX(event_ts)                                               AS last_txn_at
FROM {{ ref('stg_transactions') }}
GROUP BY DATE(event_ts), user_id
HAVING SUM(CASE WHEN is_fraud_flag = TRUE THEN 1 ELSE 0 END) > 0
ORDER BY fraud_count DESC
