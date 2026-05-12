import logging
import random
from datetime import datetime, timezone, timedelta
from faker import Faker
from db import get_connection, bulk_insert, log_run

log = logging.getLogger(__name__)
fake = Faker("ru_RU")

KZ_CITIES    = ["Астана", "Алматы", "Шымкент", "Қарағанды", "Актобе", "Тараз", "Павлодар"]
MERCHANTS    = ["Magnum", "Technodom", "Sulpak", "KFC", "Burger King", "Beeline", "Kaspi"]
CATEGORIES   = ["продукты", "электроника", "фастфуд", "связь", "одежда", "транспорт", "здоровье"]
CHANNELS     = ["mobile", "web", "pos", "atm"]
STATUSES     = ["approved", "approved", "approved", "declined", "pending"]  # 60% approved
EVENT_TYPES  = ["page_view", "page_view", "click", "search", "add_to_cart", "purchase"]
SENSOR_TYPES = ["temperature", "humidity", "pressure", "air_quality"]

def _random_ts(minutes_back=360):
    delta = random.randint(0, minutes_back * 60)
    return datetime.now(timezone.utc) - timedelta(seconds=delta)

# ── Транзакции ────────────────────────────────────────────
def _gen_transactions(n=50):
    rows = []
    for _ in range(n):
        amount = round(random.uniform(500, 150_000), 2)
        status = random.choice(STATUSES)
        is_fraud = (amount > 100_000 and status == "approved" and random.random() < 0.1)
        rows.append((
            _random_ts(),
            fake.uuid4(),
            fake.uuid4()[:8],
            round(amount, 2),
            "KZT",
            fake.uuid4()[:8],
            random.choice(MERCHANTS),
            random.choice(CATEGORIES),
            random.choice(KZ_CITIES),
            random.choice(CHANNELS),
            status,
            is_fraud,
        ))
    return rows

TXN_COLS = [
    "event_ts", "user_id", "session_id", "amount_kzt", "currency",
    "merchant_id", "merchant_name", "category", "city",
    "channel", "status", "is_fraud_flag"
]

# ── Клики ─────────────────────────────────────────────────
def _gen_clicks(n=80):
    rows = []
    for _ in range(n):
        rows.append((
            _random_ts(),
            fake.uuid4()[:12],
            fake.uuid4()[:8],
            random.choice(EVENT_TYPES),
            f"https://example.kz/{fake.uri_path()}",
            random.choice(["google.com", "instagram.com", "direct", None]),
            random.choice(["mobile", "desktop", "tablet"]),
            random.choice(["Android", "iOS", "Windows"]),
            "KZ",
            random.choice(KZ_CITIES),
            random.randint(5, 300),
        ))
    return rows

CLICK_COLS = [
    "event_ts", "session_id", "user_id", "event_type",
    "page_url", "referrer", "device_type", "os",
    "country", "city", "duration_sec"
]

# ── IoT датчики ───────────────────────────────────────────
def _gen_iot(n=30):
    rows = []
    for _ in range(n):
        city    = random.choice(KZ_CITIES)
        stype   = random.choice(SENSOR_TYPES)
        value   = {
            "temperature": round(random.uniform(-30, 40), 2),
            "humidity":    round(random.uniform(20, 95), 2),
            "pressure":    round(random.uniform(900, 1050), 2),
            "air_quality": round(random.uniform(0, 300), 2),
        }[stype]
        unit    = {"temperature": "°C", "humidity": "%",
                   "pressure": "hPa", "air_quality": "AQI"}[stype]
        anomaly = (stype == "temperature" and abs(value) > 35) or \
                  (stype == "air_quality"  and value > 200)
        rows.append((
            _random_ts(),
            f"sensor_{city[:3].upper()}_{random.randint(1,20):02d}",
            stype,
            city,
            round(random.uniform(40, 75), 4),
            round(random.uniform(50, 80), 4),
            value,
            unit,
            anomaly,
            random.randint(10, 100),
        ))
    return rows

IOT_COLS = [
    "event_ts", "sensor_id", "sensor_type", "location_city",
    "latitude", "longitude", "value", "unit",
    "is_anomaly", "battery_pct"
]

# ── Главная функция ───────────────────────────────────────
def ingest_events(conn=None):
    if conn is None:
        conn = get_connection()

    t = bulk_insert(conn, "raw.events_transactions", _gen_transactions(50), TXN_COLS)
    c = bulk_insert(conn, "raw.events_clickstream",  _gen_clicks(80),       CLICK_COLS)
    i = bulk_insert(conn, "raw.events_iot_sensors",  _gen_iot(30),          IOT_COLS)

    total = t + c + i
    log_run(conn, "event_generator", "success", rows=total)
    log.info("events: txn=%d  clicks=%d  iot=%d", t, c, i)
    return total
