import logging
from db import get_connection
from sources.crypto_api      import ingest_crypto
from sources.nbk_forex       import ingest_forex
from sources.weather_api     import ingest_weather
from sources.event_generator import ingest_events
from sources.tengri_scraper  import ingest_tengri
from sources.kafka_producer  import ingest_kafka_producer
from sources.kafka_consumer  import ingest_kafka_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("run_all")

SOURCES = [
    ("crypto",          ingest_crypto),
    ("forex_nbk",       ingest_forex),
    ("weather",         ingest_weather),
    ("event_generator", ingest_events),
    ("tengri_scraper",  ingest_tengri),
    ("kafka_producer",  ingest_kafka_producer),
    ("kafka_consumer",  ingest_kafka_consumer),
]

def main():
    log.info("===== Старт ingestion =====")
    conn = get_connection()
    log.info("Подключение к Neon: OK")

    results = {}
    for name, fn in SOURCES:
        try:
            results[name] = fn(conn)
        except Exception as e:
            log.error("%-18s ОШИБКА: %s", name, e)
            results[name] = 0

    conn.close()

    log.info("===== Итог =====")
    for name, n in results.items():
        log.info("  %-18s  %d строк", name, n)
    log.info("================")

if __name__ == "__main__":
    main()