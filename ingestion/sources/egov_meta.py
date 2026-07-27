import requests
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
EGOV_URL = "https://data.egov.kz"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

def get_all_api_uris():
    """Берём все api_uri из таблицы которую уже загрузили"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT api_uri FROM raw.egov_datasets")
    uris = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return uris

def get_meta(api_uri):
    """Получаем метаданные одного датасета — без API ключа!"""
    try:
        response = requests.get(
            f"{EGOV_URL}/meta/{api_uri}/v3",
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Ошибка для {api_uri}: {e}")
        return None

def save_meta(api_uri, meta):
    """Сохраняем метаданные в новую таблицу"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS raw.egov_meta (
                                                             api_uri TEXT PRIMARY KEY,
                                                             description_ru TEXT,
                                                             modified_date TEXT,
                                                             actual BOOLEAN,
                                                             fields_count INTEGER,
                                                             responsible_email TEXT,
                                                             loaded_at TIMESTAMP DEFAULT NOW()
                )
                """)

    cur.execute("""
                INSERT INTO raw.egov_meta
                (api_uri, description_ru, modified_date, actual, fields_count, responsible_email)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (api_uri) DO NOTHING
                """, (
                    api_uri,
                    meta.get("descriptionRu"),
                    meta.get("modifiedDate"),
                    meta.get("actual"),
                    len(meta.get("fields", {})),
                    meta.get("responsible", {}).get("email")
                ))

    conn.commit()
    cur.close()
    conn.close()

def main():
    uris = get_all_api_uris()
    print(f"Всего датасетов для обработки: {len(uris)}")

    for i, uri in enumerate(uris):
        meta = get_meta(uri)

        if meta:
            save_meta(uri, meta)

        # Прогресс каждые 100
        if (i + 1) % 100 == 0:
            print(f"Обработано: {i + 1}/{len(uris)}")

        # Пауза чтобы не перегружать сервер
        time.sleep(0.1)

    print("Готово!")

if __name__ == "__main__":
    main()
