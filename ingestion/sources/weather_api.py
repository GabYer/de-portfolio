import sys
import logging
from db import get_connection
from sources.crypto_api import ingest_crypto
from sources.nbk_forex import ingest_forex

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("run_all")

def main():
    log.info("===== Старт ingestion =====")
    conn = get_connection()
    log.info("Подключение к Neon: OK")

    results = {}

    try:
        results["crypto"] = ingest_crypto(conn)
    except Exception as e:
        log.error("crypto ОШИБКА: %s", e)
        results["crypto"] = 0

    try:
        results["forex_nbk"] = ingest_forex(conn)
    except Exception as e:
        log.error("forex_nbk ОШИБКА: %s", e)
        results["forex_nbk"] = 0

    conn.close()

    log.info("===== Итог =====")
    for name, n in results.items():
        log.info("  %-15s  %d строк", name, n)
    log.info("================")

if __name__ == "__main__":
    main()
