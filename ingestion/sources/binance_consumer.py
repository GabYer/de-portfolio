import asyncio
import json
import logging
import websockets
import clickhouse_connect
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

log = logging.getLogger(__name__)
load_dotenv("/data/de-portfolio/.env")

# Символы для отслеживания
SYMBOLS = ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"]

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "100.112.75.57")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "admin")
CLICKHOUSE_PASS = os.getenv("CLICKHOUSE_PASS")
CLICKHOUSE_DB   = os.getenv("CLICKHOUSE_DB", "trading")

def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASS,
        database=CLICKHOUSE_DB,
    )

def build_ws_url(symbols: list) -> str:
    streams = "/".join(f"{s}@trade" for s in symbols)
    return f"wss://stream.binance.com:9443/stream?streams={streams}"

async def consume(duration_seconds=60):
    url = build_ws_url(SYMBOLS)
    rows = []
    client = get_client()

    log.info("Подключаемся к Binance WebSocket: %d символов", len(SYMBOLS))
    log.info("URL: %s", url)

    start = asyncio.get_event_loop().time()

    async with websockets.connect(url, ping_interval=20) as ws:
        log.info("Подключение установлено!")
        async for message in ws:
            data = json.loads(message)
            trade = data.get("data", {})

            if trade.get("e") != "trade":
                continue

            rows.append([
                int(trade["t"]),                          # trade_id
                trade["s"],                               # symbol
                float(trade["p"]),                        # price
                float(trade["q"]),                        # quantity
                float(trade["p"]) * float(trade["q"]),   # quote_quantity
                datetime.fromtimestamp(
                    trade["T"] / 1000, tz=timezone.utc
                ),                                        # trade_time
                bool(trade["m"]),                         # is_buyer_maker
            ])

            # Вставляем батчами по 100 строк
            if len(rows) >= 100:
                client.insert(
                    "binance_trades",
                    rows,
                    column_names=[
                        "trade_id", "symbol", "price",
                        "quantity", "quote_quantity",
                        "trade_time", "is_buyer_maker"
                    ]
                )
                log.info("Вставлено %d трейдов в ClickHouse", len(rows))
                rows.clear()

            # Останавливаемся через duration_seconds
            if asyncio.get_event_loop().time() - start > duration_seconds:
                break

    # Вставляем остаток
    if rows:
        client.insert(
            "binance_trades",
            rows,
            column_names=[
                "trade_id", "symbol", "price",
                "quantity", "quote_quantity",
                "trade_time", "is_buyer_maker"
            ]
        )
        log.info("Финальный батч: %d трейдов", len(rows))

    client.close()
    log.info("Binance consumer завершён")

def ingest_binance(conn=None):
    """Совместимость с run_all.py — conn не используется"""
    try:
        asyncio.run(consume(duration_seconds=60))
        return 1
    except Exception as e:
        log.error("binance_consumer ОШИБКА: %s", e)
        return 0

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
    )
    asyncio.run(consume(duration_seconds=60))
