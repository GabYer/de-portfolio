{{ config(materialized='table') }}

SELECT DISTINCT ON (url)
    url,
    TRIM(title)                     AS title,
    INITCAP(TRIM(category))         AS category,
    description,
    published_at,
    scraped_at
FROM {{ source('raw', 'tengri_news') }}
WHERE title IS NOT NULL
  AND LENGTH(TRIM(title)) > 10
  AND published_at >= NOW() - INTERVAL '7 days'
ORDER BY url, scraped_at DESC
