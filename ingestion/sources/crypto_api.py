import requests
import time
import logging
from db import get_connection, bulk_insert, log_run

log = logging.getLogger(__name__)

URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd"
    "&ids=bitcoin,ethereum,binancecoin"
    "&order=market_cap_desc"
    "&sparkline=false"
)

def ingest_crypto(conn=None):
    if conn is None:
        conn = get_connection()

    for attempt in range(3):
        try:
            resp = requests.get(URL, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            break
        except Exception as e:
            log.warning("Попытка %d: %s", attempt + 1, e)
            time.sleep(5)
    else:
        log_run(conn, "crypto", "failed", error="Не удалось получить данные")
        return 0

    rows = []
    for c in data:
        rows.append((
            c.get("id"),
            c.get("name"),
            c.get("symbol", "").upper(),
            c.get("current_price"),
            c.get("market_cap"),
            c.get("total_volume"),
            c.get("price_change_24h"),
            c.get("price_change_percentage_24h"),
            c.get("circulating_supply"),
            c.get("ath"),
            c.get("ath_date"),
            c.get("last_updated"),
        ))

    cols = [
        "coin_id", "coin_name", "symbol",
        "current_price_usd", "market_cap_usd", "total_volume_usd",
        "price_change_24h", "price_change_pct_24h",
        "circulating_supply", "ath_usd", "ath_date", "source_snapshot_at"
    ]

    n = bulk_insert(conn, "raw.crypto_prices", rows, cols)
    log_run(conn, "crypto", "success", rows=n)
    log.info("crypto: загружено %d монет", n)
    return n
