{{ config(materialized='view') }}

SELECT
    DATE(published_at)              AS pub_date,
    category,
    COUNT(*)                        AS articles_count
FROM {{ ref('stg_news') }}
GROUP BY DATE(published_at), category
ORDER BY pub_date DESC, articles_count DESC
