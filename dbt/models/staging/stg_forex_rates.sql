{{ config(materialized='table') }}

SELECT DISTINCT ON (rate_date, currency_code)
    rate_date,
    UPPER(TRIM(currency_code))      AS currency_code,
    INITCAP(TRIM(currency_name))    AS currency_name,
    COALESCE(units, 1)              AS units,
    rate_kzt,
    change_kzt,
    loaded_at
FROM {{ source('raw', 'forex_rates_nbk') }}
WHERE rate_kzt > 0
  AND currency_code IS NOT NULL
ORDER BY rate_date, currency_code, loaded_at DESC
