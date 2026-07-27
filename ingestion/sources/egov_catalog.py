import requests
import psycopg2
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (там хранится DATABASE_URL)
load_dotenv()

# Константы
EGOV_URL = "https://data.egov.kz"
DATABASE_URL = os.getenv("DATABASE_URL")
# Заголовки чтобы сервер думал что мы браузер
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://data.egov.kz/datasets/listbycategory"
}

def get_total_count():
    response = requests.post(
        f"{EGOV_URL}/datasets/getdatasetsrecount",
        data={"status": "PUBLISHED"},
        headers=HEADERS
    )
    print(f"Статус ответа: {response.status_code}")
    print(f"Текст ответа: {response.text}")
    data = response.json()
    return data["totalCount"]

def get_datasets_page(page, count=100):
    response = requests.post(
        f"{EGOV_URL}/datasets/getdatasetsre",
        data={
            "page": page,
            "count": count,
            "status": "PUBLISHED",
            "byGovAgencyId": "",
            "categoryId": "",
            "statusType": "",
            "datasetSortSelect": "2"
        },
        headers=HEADERS
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text[:300]}")
    return response.json()

def save_to_db(datasets):
    """Сохраняем датасеты в Neon PostgreSQL"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Создаём таблицу если её нет
    cur.execute("""
                CREATE TABLE IF NOT EXISTS raw.egov_datasets (
                                                                 api_uri TEXT PRIMARY KEY,
                                                                 name_ru TEXT,
                                                                 name_kk TEXT,
                                                                 created_date TEXT,
                                                                 loaded_at TIMESTAMP DEFAULT NOW()
                )
                """)

    # Вставляем каждый датасет
    for d in datasets:
        cur.execute("""
                    INSERT INTO raw.egov_datasets (api_uri, name_ru, name_kk, created_date)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (api_uri) DO NOTHING
                    """, (
                        d.get("apiUri"),
                        d.get("nameRu"),
                        d.get("nameKk"),
                        d.get("createdDate")
                    ))

    conn.commit()
    cur.close()
    conn.close()

def main():
    print("Считаем датасеты...")
    total = get_total_count()
    print(f"Всего датасетов: {total}")

    page = 1
    count = 100
    total_saved = 0

    while True:
        result = get_datasets_page(page, count)
        datasets = result.get("datasets", [])

        if not datasets:
            break

        save_to_db(datasets)
        total_saved += len(datasets)

        # Прогресс каждые 10 страниц
        if page % 10 == 0:
            print(f"Прогресс: {total_saved}/{total}")

        page += 1

    print(f"Готово! Всего сохранено: {total_saved} датасетов")

# Запускаем только если файл запущен напрямую
if __name__ == "__main__":
    main()