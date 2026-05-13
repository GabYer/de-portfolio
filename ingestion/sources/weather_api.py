import requests
import logging
import time
from datetime import datetime, timezone
from db import get_connection, bulk_insert, log_run

log = logging.getLogger(__name__)

CITIES = [
    {"name": "Астана",  "lat": 51.1801, "lon": 71.4460},
    {"name": "Алматы",  "lat": 43.2220, "lon": 76.8512},
    {"name": "Шымкент", "lat": 42.3000, "lon": 69.6000},
]

BASE_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,relative_humidity_2m,"
    "wind_speed_10m,precipitation,weather_code"
    "&timezone=Asia%2FAlmaty"
)

def _fetch_with_retry(url, retries=3, timeout=30):
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            log.warning("Попытка %d/%d: %s", attempt, retries, e)
            if attempt < retries:
                time.sleep(5)
    return None

def ingest_weather(conn=None):
    if conn is None:
        conn = get_connection()

    rows = []
    now = datetime.now(timezone.utc)

    for city in CITIES:
        url = BASE_URL.format(lat=city["lat"], lon=city["lon"])
        data = _fetch_with_retry(url)
        if not data:
            log.warning("weather %s — пропускаем", city["name"])
            continue

        cur = data.get("current", {})
        rows.append((
            now,
            city["name"],
            city["lat"],
            city["lon"],
            cur.get("temperature_2m"),
            cur.get("relative_humidity_2m"),
            cur.get("wind_speed_10m"),
            cur.get("precipitation"),
            cur.get("weather_code"),
        ))

    cols = [
        "observed_at", "city", "latitude", "longitude",
        "temp_celsius", "humidity_pct", "wind_speed_ms",
        "precipitation", "weather_code"
    ]

    n = bulk_insert(conn, "raw.weather_astana", rows, cols)
    log_run(conn, "weather", "success", rows=n)
    log.info("weather: загружено %d городов", n)
    return n
