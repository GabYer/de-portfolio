import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone

import clickhouse_connect
import websockets
from dotenv import load_dotenv

load_dotenv("/data/de-portfolio/.env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

SYMBOLS = ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"]

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "100.112.75.57")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "admin")
CLICKHOUSE_PASS = os.getenv("CLICKHOUSE_PASS")
CLICKHOUSE_DB   = os.getenv("CLICKHOUSE_DB", "trading")

BATCH_SIZE      = 100
RECONNECT_DELAY = 5

def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASS,
        database=CLICKHOUSE_DB,
    )

def insert_batch(client, rows):
    client.insert(
        "binance_trades",
        rows,
        column_names=[
            "trade_id", "symbol", "price",
            "quantity", "quote_quantity",
            "trade_time", "is_buyer_maker"
        ]
    )
    log.info("Вставлено %d трейдов", len(rows))

def build_ws_url(symbols: list) -> str:
    streams = "/".join(f"{s}@trade" for s in symbols)
    return f"wss://stream.binance.com:9443/stream?streams={streams}"

async def consume():
    url = build_ws_url(SYMBOLS)
    log.info("Старт Binance 24/7 stream — %d символов", len(SYMBOLS))

    while True:
        rows = []
        try:
            client = get_client()
            log.info("ClickHouse подключён")
            async with websockets.connect(url, ping_interval=20) as ws:
                log.info("WebSocket подключён")
                async for message in ws:
                    data = json.loads(message)
                    trade = data.get("data", {})

                    if trade.get("e") != "trade":
                        continue

                    rows.append([
                        int(trade["t"]),
                        trade["s"],
                        float(trade["p"]),
                        float(trade["q"]),
                        float(trade["p"]) * float(trade["q"]),
                        datetime.fromtimestamp(trade["T"] / 1000, tz=timezone.utc),
                        bool(trade["m"]),
                    ])

                    if len(rows) >= BATCH_SIZE:
                        insert_batch(client, rows)
                        rows.clear()

        except Exception as e:
            log.error("Ошибка: %s", e)
            if rows:
                try:
                    insert_batch(client, rows)
                except Exception:
                    pass
            log.info("Реконнект через %d сек...", RECONNECT_DELAY)
            await asyncio.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    asyncio.run(consume())

