import json
import random
import logging
from datetime import datetime, timezone, timedelta
from faker import Faker
from kafka import KafkaProducer

log = logging.getLogger(__name__)
fake = Faker("ru_RU")

KZ_CITIES     = ["Астана", "Алматы", "Шымкент", "Қарағанды", "Актобе", "Павлодар"]
MERCHANTS     = ["Magnum", "Technodom", "Sulpak", "KFC", "Kaspi", "Beeline"]
CATEGORIES    = ["продукты", "электроника", "фастфуд", "связь", "одежда", "транспорт"]
CHANNELS      = ["mobile", "web", "pos", "atm"]
STATUSES      = ["approved", "approved", "approved", "declined", "pending"]
EVENT_TYPES   = ["page_view", "page_view", "click", "search", "add_to_cart", "purchase"]
SENSOR_TYPES  = ["temperature", "humidity", "pressure", "air_quality"]

KAFKA_BROKER  = "100.112.75.57:9092"

def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False, default=str).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )

def _random_ts():
    return datetime.now(timezone.utc).isoformat()

def produce_transactions(producer, n=50):
    for _ in range(n):
        amount = round(random.uniform(500, 150_000), 2)
        status = random.choice(STATUSES)
        event = {
            "event_id":      fake.uuid4(),
            "event_ts":      _random_ts(),
            "user_id":       fake.uuid4()[:8],
            "session_id":    fake.uuid4()[:8],
            "amount_kzt":    amount,
            "currency":      "KZT",
            "merchant_name": random.choice(MERCHANTS),
            "category":      random.choice(CATEGORIES),
            "city":          random.choice(KZ_CITIES),
            "channel":       random.choice(CHANNELS),
            "status":        status,
            "is_fraud_flag": amount > 100_000 and status == "approved" and random.random() < 0.1,
        }
        producer.send("transactions", key=event["user_id"], value=event)
    producer.flush()
    log.info("kafka: отправлено %d транзакций", n)
    return n

def produce_clickstream(producer, n=80):
    for _ in range(n):
        event = {
            "event_id":    fake.uuid4(),
            "event_ts":    _random_ts(),
            "session_id":  fake.uuid4()[:12],
            "user_id":     fake.uuid4()[:8],
            "event_type":  random.choice(EVENT_TYPES),
            "page_url":    f"https://example.kz/{fake.uri_path()}",
            "device_type": random.choice(["mobile", "desktop", "tablet"]),
            "city":        random.choice(KZ_CITIES),
            "country":     "KZ",
        }
        producer.send("clickstream", key=event["session_id"], value=event)
    producer.flush()
    log.info("kafka: отправлено %d кликов", n)
    return n

def produce_iot(producer, n=30):
    for _ in range(n):
        city   = random.choice(KZ_CITIES)
        stype  = random.choice(SENSOR_TYPES)
        value  = {
            "temperature": round(random.uniform(-30, 40), 2),
            "humidity":    round(random.uniform(20, 95), 2),
            "pressure":    round(random.uniform(900, 1050), 2),
            "air_quality": round(random.uniform(0, 300), 2),
        }[stype]
        event = {
            "event_id":    fake.uuid4(),
            "event_ts":    _random_ts(),
            "sensor_id":   f"sensor_{city[:3].upper()}_{random.randint(1,20):02d}",
            "sensor_type": stype,
            "city":        city,
            "value":       value,
            "is_anomaly":  value > 35 if stype == "temperature" else value > 200,
            "battery_pct": random.randint(10, 100),
        }
        producer.send("iot_sensors", key=event["sensor_id"], value=event)
    producer.flush()
    log.info("kafka: отправлено %d IoT событий", n)
    return n

def ingest_kafka_producer(conn=None):
    """Совместимость с run_all.py — conn не используется"""
    try:
        producer = get_producer()
        t = produce_transactions(producer, 50)
        c = produce_clickstream(producer, 80)
        i = produce_iot(producer, 30)
        producer.close()
        total = t + c + i
        log.info("kafka_producer: итого %d событий", total)
        return total
    except Exception as e:
        log.error("kafka_producer ОШИБКА: %s", e)
        return 0