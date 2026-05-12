import requests
import logging
from datetime import date
from db import get_connection, bulk_insert, log_run

log = logging.getLogger(__name__)

URL = "https://nationalbank.kz/rss/get_rates.cfm?fdate="

CURRENCIES = {"USD", "EUR", "RUB", "CNY", "GBP"}

def ingest_forex(conn=None):
    if conn is None:
        conn = get_connection()

    today = date.today().strftime("%d.%m.%Y")
    try:
        resp = requests.get(URL + today, timeout=15)
        resp.encoding = "utf-8"
        text = resp.text
    except Exception as e:
        log_run(conn, "forex_nbk", "failed", error=str(e))
        return 0

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(text)
    except Exception as e:
        log_run(conn, "forex_nbk", "failed", error=f"XML ошибка: {e}")
        return 0

    rows = []
    for item in root.findall(".//item"):
        code = (item.findtext("title") or "").strip()
        if code not in CURRENCIES:
            continue
        try:
            rate = float((item.findtext("description") or "0").replace(",", "."))
            units = int(item.findtext("quant") or 1)
            name = (item.findtext("fullname") or "").strip()
            change = float((item.findtext("change") or "0").replace(",", "."))
        except ValueError:
            continue

        rows.append((
            date.today(),
            code,
            name,
            units,
            round(rate, 4),
            round(change, 4),
            URL + today,
        ))

    cols = ["rate_date", "currency_code", "currency_name",
            "units", "rate_kzt", "change_kzt", "source_url"]

    n = bulk_insert(conn, "raw.forex_rates_nbk", rows, cols)
    log_run(conn, "forex_nbk", "success", rows=n)
    log.info("forex_nbk: загружено %d валют", n)
    return n
