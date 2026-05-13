import requests
import logging
import re
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from db import get_connection, bulk_insert, log_run

log = logging.getLogger(__name__)

BASE_URL = "https://tengrinews.kz"

SECTIONS = [
    ("Экономика",    "/economics_business/"),
    ("Казахстан",    "/kazakhstan_news/"),
    ("Происшествия", "/crime/"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Любая ссылка на статью — содержит слово и цифровой ID в конце
ARTICLE_RE = re.compile(r"/[a-z_]+-\d{4,}/?$")

def _parse_date(text):
    now = datetime.now(timezone.utc)
    text = (text or "").strip()
    try:
        if text.startswith("Сегодня"):
            h, m = map(int, text.replace("Сегодня", "").strip().split(":"))
            return now.replace(hour=h, minute=m, second=0, microsecond=0)
        if text.startswith("Вчера"):
            h, m = map(int, text.replace("Вчера", "").strip().split(":"))
            return (now - timedelta(days=1)).replace(hour=h, minute=m, second=0, microsecond=0)
    except Exception:
        pass
    return now

def _parse_section(section_name, url):
    # Спорт — отдельный поддомен
    full_url = url if url.startswith("http") else BASE_URL + url
    try:
        resp = requests.get(full_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        log.warning("tengri [%s] ошибка: %s", section_name, e)
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    rows = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Фильтр — только ссылки на статьи
        if not ARTICLE_RE.search(href):
            continue

        # Пропускаем служебные ссылки
        if any(x in href for x in ["/tag/", "/page/", "/user/", "javascript", "#"]):
            continue

        full = href if href.startswith("http") else BASE_URL + href
        if full in seen:
            continue
        seen.add(full)

        title = a.get_text(strip=True)
        if not title or len(title) < 10:
            continue

        # Ищем дату рядом
        pub_date = datetime.now(timezone.utc)
        container = a.find_parent("li") or a.find_parent("div") or a.find_parent("article")
        if container:
            for txt in container.stripped_strings:
                if txt.startswith("Сегодня") or txt.startswith("Вчера"):
                    pub_date = _parse_date(txt)
                    break

        rows.append((
            full,
            title[:500],
            section_name,
            None,
            pub_date,
            datetime.now(timezone.utc),
        ))

        if len(rows) >= 30:
            break

    log.info("tengri [%s]: найдено %d новостей", section_name, len(rows))
    return rows


COLS  = ["url", "title", "category", "description", "published_at", "scraped_at"]
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
        all_rows.extend(_parse_section(section_name, url))

    if not all_rows:
        log_run(conn, "tengri_scraper", "failed", error="Нет данных")
        return 0

    n = bulk_insert(conn, TABLE, all_rows, COLS)
    log_run(conn, "tengri_scraper", "success", rows=n)
    log.info("tengri: загружено %d новостей", n)
    return n
