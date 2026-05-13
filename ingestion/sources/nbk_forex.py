import requests
import logging
from datetime import date
from db import get_connection, bulk_insert, log_run

log = logging.getLogger(__name__)

CURRENCIES = {"USD", "EUR", "RUB", "CNY", "GBP"}

def ingest_forex(conn=None):
    if conn is None:
        conn = get_connection()

    today = date.today().strftime("%d.%m.%Y")
    url = f"https://nationalbank.kz/rss/get_rates.cfm?fdate={today}"

    try:
        resp = requests.get(url, timeout=20)
        resp.encoding = "utf-8"
        log.info("forex_nbk: HTTP %d, длина ответа %d байт", resp.status_code, len(resp.text))
        log.info("forex_nbk: первые 300 символов: %s", resp.text[:300])
    except Exception as e:
        log.error("forex_nbk: ошибка запроса: %s", e)
        log_run(conn, "forex_nbk", "failed", error=str(e))
        return 0

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(resp.text)
        log.info("forex_nbk: корневой тег = %s", root.tag)
        all_items = root.findall(".//item")
        log.info("forex_nbk: найдено item элементов = %d", len(all_items))
        # Логируем первый элемент для диагностики
        if all_items:
            first = all_items[0]
            for child in first:
                log.info("  тег: %-15s  текст: %s", child.tag, child.text)
    except Exception as e:
        log.error("forex_nbk: XML ошибка: %s", e)
        log_run(conn, "forex_nbk", "failed", error=str(e))
        return 0

    rows = []
    for item in root.findall(".//item"):
        code = (item.findtext("title") or "").strip()
        if code not in CURRENCIES:
            continue
        try:
            rate   = float((item.findtext("description") or "0").replace(",", "."))
            units  = int(item.findtext("quant") or 1)
            name   = (item.findtext("fullname") or "").strip()
            change = float((item.findtext("change") or "0").replace(",", "."))
        except ValueError as e:
            log.warning("forex_nbk: ошибка парсинга %s: %s", code, e)
            continue

        rows.append((date.today(), code, name, units, round(rate, 4), round(change, 4), url))

    log.info("forex_nbk: отфильтровано строк = %d", len(rows))

    if not rows:
        log_run(conn, "forex_nbk", "failed", error="Нет данных после фильтрации")
        return 0

    cols = ["rate_date", "currency_code", "currency_name",
            "units", "rate_kzt", "change_kzt", "source_url"]
    n = bulk_insert(conn, "raw.forex_rates_nbk", rows, cols)
    log_run(conn, "forex_nbk", "success", rows=n)
    log.info("forex_nbk: загружено %d валют", n)
    return n