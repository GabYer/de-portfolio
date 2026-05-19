import json
import logging
from datetime import datetime, timezone
from kafka import KafkaConsumer as _KafkaConsumer
from db import get_connection, bulk_insert, log_run

log = logging.getLogger(__name__)

KAFKA_BROKER = "100.112.75.57:9092"

TOPIC_TABLE_MAP = {
    "transactions": {
        "table": "raw.events_transactions",
        "cols": [
            "event_ts", "user_id", "session_id", "amount_kzt",
            "currency", "merchant_name", "category", "city",
            "channel", "status", "is_fraud_flag"
        ],
    },
    "clickstream": {
        "table": "raw.events_clickstream",
        "cols": [
            "event_ts", "session_id", "user_id", "event_type",
            "page_url", "device_type", "city", "country"
        ],
    },
    "iot_sensors": {
        "table": "raw.events_iot_sensors",
        "cols": [
            "event_ts", "sensor_id", "sensor_type",
            "location_city", "value", "is_anomaly", "battery_pct"
        ],
    },
}

def _parse_row(topic, msg):
    d = msg
    if topic == "transactions":
        return (
            d.get("event_ts"), d.get("user_id"), d.get("session_id"),
            d.get("amount_kzt"), d.get("currency", "KZT"),
            d.get("merchant_name"), d.get("category"),
            d.get("city"), d.get("channel"), d.get("status"),
            d.get("is_fraud_flag", False),
        )
    elif topic == "clickstream":
        return (
            d.get("event_ts"), d.get("session_id"), d.get("user_id"),
            d.get("event_type"), d.get("page_url"),
            d.get("device_type"), d.get("city"), d.get("country", "KZ"),
        )
    elif topic == "iot_sensors":
        return (
            d.get("event_ts"), d.get("sensor_id"), d.get("sensor_type"),
            d.get("city"), d.get("value"),
            d.get("is_anomaly", False), d.get("battery_pct"),
        )

def consume_topic(conn, topic, timeout_ms=5000):
    cfg = TOPIC_TABLE_MAP[topic]
    consumer = _KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=f"de_portfolio_{topic}",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=timeout_ms,
    )
    rows = []
    for msg in consumer:
        row = _parse_row(topic, msg.value)
        if row:
            rows.append(row)
    consumer.close()

    if rows:
        n = bulk_insert(conn, cfg["table"], rows, cfg["cols"])
        log.info("kafka_consumer [%s]: записано %d строк", topic, n)
        return n
    log.info("kafka_consumer [%s]: нет новых сообщений", topic)
    return 0

def ingest_kafka_consumer(conn=None):
    if conn is None:
        conn = get_connection()
    total = 0
    for topic in TOPIC_TABLE_MAP:
        try:
            total += consume_topic(conn, topic)
        except Exception as e:
            log.error("kafka_consumer [%s] ОШИБКА: %s", topic, e)
    log_run(conn, "kafka_consumer", "success", rows=total)
    return total