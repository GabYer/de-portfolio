import requests
import logging
import re
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

# Категории по URL — определяем по части пути
URL_CATEGORY_MAP = {
    "kazakhstan_news": "Казахстан",
    "economics_business": "Экономика",
    "world_news": "Мир",
    "sport": "Спорт",
    "politics": "Политика",
    "crime": "Происшествия",
}

def _detect_category(href, default):
    for key, cat in URL_CATEGORY_MAP.items():
        if key in href:
            return cat
    return default

def _parse_date(text):
    """Парсим 'Сегодня 01:43' или 'Вчера 22:14' или '12 мая 10:30'"""
    now = datetime.now(timezone.utc)
    text = text.strip()
    try:
        if text.startswith("Сегодня"):
            time_part = text.replace("Сегодня", "").strip()
            h, m = map(int, time_part.split(":"))
            return now.replace(hour=h, minute=m, second=0, microsecond=0)
        if text.startswith("Вчера"):
            from datetime import timedelta
            time_part = text.replace("Вчера", "").strip()
            h, m = map(int, time_part.split(":"))
            yesterday = now - timedelta(days=1)
            return yesterday.replace(hour=h, minute=m, second=0, microsecond=0)
    except Exception:
        pass
    return now

def _parse_section(section_name, url):
    try:
        resp = requests.get(BASE_URL + url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        log.warning("tengri [%s] ошибка запроса: %s", section_name, e)
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    rows = []
    seen_urls = set()

    # Ищем все ссылки на новости — /kazakhstan_news/, /news/, /world_news/ и т.д.
    news_pattern = re.compile(
        r"/(kazakhstan_news|world_news|economics_business|sport|politics|crime|news)/[a-z0-9_-]+-\d+"
    )

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # Только ссылки на статьи (с числовым ID в конце)
        if not news_pattern.search(href):
            continue

        # Полный URL
        full_url = href if href.startswith("http") else BASE_URL + href

        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        # Заголовок — текст ссылки, убираем иконки
        title = a_tag.get_text(strip=True)
        if not title or len(title) < 10:
            continue

        # Дата — ищем ближайший элемент с датой рядом с новостью
        pub_date = datetime.now(timezone.utc)
        parent = a_tag.find_parent()
        if parent:
            # Ищем текст с датой в родительском блоке
            for sibling in parent.find_all(string=True):
                s = sibling.strip()
                if s.startswith("Сегодня") or s.startswith("Вчера"):
                    pub_date = _parse_date(s)
                    break

        category = _detect_category(href, section_name)

        rows.append((
            full_url,
            title[:500],
            category,
            None,
            pub_date,
            datetime.now(timezone.utc),
        ))

        if len(rows) >= 30:
            break

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

    n = bulk_insert(conn, TABLE, all_rows, COLS)
    log_run(conn, "tengri_scraper", "success", rows=n)
    log.info("tengri: загружено %d новостей", n)
    return n
