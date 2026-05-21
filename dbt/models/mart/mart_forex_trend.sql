{{ config(materialized='view') }}

SELECT
    rate_date,
    currency_code,
    currency_name,
    ROUND((rate_kzt / NULLIF(units,0))::NUMERIC, 4)             AS rate_per_unit,
    ROUND((rate_kzt / NULLIF(units,0) - LAG(rate_kzt / NULLIF(units,0)) OVER (
        PARTITION BY currency_code ORDER BY rate_date
    ))::NUMERIC, 4)                                             AS day_change,
    loaded_at
FROM {{ ref('stg_forex_rates') }}
ORDER BY rate_date DESC, currency_code
