import requests
import logging
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from db import get_connection, bulk_insert, log_run

log = logging.getLogger(__name__)

BASE_URL = "https://tengrinews.kz"
SECTIONS = [
    ("Новости",   "/news/"),
    ("Экономика", "/economics_business/"),
    ("Спорт",     "/sport/"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def _parse_section(section_name, url):
    try:
        resp = requests.get(BASE_URL + url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        log.warning("tengri [%s] ошибка: %s", section_name, e)
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    items = soup.select(".content-main-list-item, .news-list-item, li.item")
    if not items:
        # Запасной селектор
        items = soup.select("article, .tn-news-item")

    rows = []
    for item in items[:30]:
        try:
            # Заголовок
            title_tag = item.select_one("a.item-title, .title a, h2 a, h3 a, a[href*='/news/']")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href  = title_tag.get("href", "")
            if not href.startswith("http"):
                href = BASE_URL + href
            if not title or len(title) < 5:
                continue

            # Дата
            time_tag = item.select_one("time, .date, .time, [datetime]")
            pub_date = None
            if time_tag:
                dt_str = time_tag.get("datetime") or time_tag.get_text(strip=True)
                try:
                    pub_date = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                except Exception:
                    pub_date = datetime.now(timezone.utc)

            # Описание
            desc_tag = item.select_one(".item-text, .announce, p")
            description = desc_tag.get_text(strip=True)[:500] if desc_tag else None

            rows.append((
                href,
                title,
                section_name,
                description,
                pub_date or datetime.now(timezone.utc),
                datetime.now(timezone.utc),
            ))
        except Exception as e:
            log.debug("Пропускаем элемент: %s", e)
            continue

    log.info("tengri [%s]: найдено %d новостей", section_name, len(rows))
    return rows


COLS = ["url", "title", "category", "description", "published_at", "scraped_at"]

TABLE = "raw.tengri_news"

DDL = """
CREATE TABLE IF NOT EXISTS raw.tengri_news (
    id            BIGSERIAL PRIMARY KEY,
    loaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    url           TEXT        NOT NULL,
    title         TEXT        NOT NULL,
    category      TEXT,
    description   TEXT,
    published_at  TIMESTAMPTZ,
    scraped_at    TIMESTAMPTZ NOT NULL,
    UNIQUE(url)
);
"""

def ingest_tengri(conn=None):
    if conn is None:
        conn = get_connection()

    # Создаём таблицу если не существует
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()

    all_rows = []
    for section_name, url in SECTIONS:
        rows = _parse_section(section_name, url)
        all_rows.extend(rows)

    if not all_rows:
        log_run(conn, "tengri_scraper", "failed", error="Нет данных")
        return 0

    # UNIQUE(url) — дубликаты игнорируются автоматически
    n = bulk_insert(conn, TABLE, all_rows, COLS)
    log_run(conn, "tengri_scraper", "success", rows=n)
    log.info("tengri: загружено %d новостей", n)
    return n
