import requests
import psycopg2
import clickhouse_connect
import os
import time
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
EGOV_API_KEY = "aa2a3111274e4bad8c5cea2660666b87"
EGOV_URL = "https://data.egov.kz"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

def get_ch_client():
    """Подключение к ClickHouse"""
    return clickhouse_connect.get_client(
        host='ch-api.gabyer.dev',
        port=443,
        secure=True,
        username='admin',
        password='123qweASDasd'
    )

def get_datasets_with_meta():
    """Берём датасеты у которых есть метаданные (знаем схему полей)"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
                SELECT d.api_uri, d.name_ru
                FROM raw.egov_datasets d
                         JOIN raw.egov_meta m ON d.api_uri = m.api_uri
                WHERE m.fields_count > 0
                LIMIT 50
                """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_field_labels(api_uri):
    """Получаем названия полей из метаданных"""
    try:
        response = requests.get(
            f"{EGOV_URL}/meta/{api_uri}/v3",
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            meta = response.json()
            # Возвращаем словарь: column_name → {label, type}
            fields = {}
            for col_name, col_info in meta.get("fields", {}).items():
                fields[col_name] = {
                    "label": col_info.get("labelRu") or col_name,
                    "type": col_info.get("type", "String")
                }
            return fields
    except Exception as e:
        print(f"Ошибка метаданных {api_uri}: {e}")
    return {}

def get_dataset_data(api_uri, size=100):
    """Получаем реальные данные датасета через API"""
    try:
        import json
        source = json.dumps({"size": size})
        response = requests.get(
            f"{EGOV_URL}/api/v4/{api_uri}/v3",
            params={
                "apiKey": EGOV_API_KEY,
                "source": source
            },
            headers=HEADERS,
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Ошибка данных {api_uri}: {e}")
    return []

def save_to_clickhouse(ch, rows):
    """Пишем батч строк в ClickHouse"""
    if not rows:
        return
    ch.insert(
        'egov.dataset_values',
        rows,
        column_names=[
            'dataset_uri', 'dataset_name', 'row_num',
            'column_name', 'column_label', 'column_type', 'value'
        ]
    )

def process_dataset(ch, api_uri, dataset_name):
    """Обрабатываем один датасет"""
    # Получаем схему полей
    fields = get_field_labels(api_uri)
    if not fields:
        print(f"  Нет схемы для {api_uri}")
        return 0

    # Получаем данные
    data = get_dataset_data(api_uri)
    if not data:
        print(f"  Нет данных для {api_uri}")
        return 0

    # Преобразуем в EAV формат
    rows = []
    for row_num, record in enumerate(data):
        for col_name, value in record.items():
            if col_name == 'id':
                continue  # пропускаем системный id
            field_info = fields.get(col_name, {"label": col_name, "type": "String"})
            rows.append([
                api_uri,
                dataset_name or "",
                row_num,
                col_name,
                field_info["label"],
                field_info["type"],
                str(value) if value is not None else ""
            ])

    save_to_clickhouse(ch, rows)
    return len(data)

def main():
    print("Подключаемся к ClickHouse...")
    ch = get_ch_client()

    print("Берём список датасетов...")
    datasets = get_datasets_with_meta()
    print(f"Датасетов для обработки: {len(datasets)}")

    total_records = 0

    for i, (api_uri, name_ru) in enumerate(datasets):
        print(f"[{i+1}/{len(datasets)}] {api_uri}")
        count = process_dataset(ch, api_uri, name_ru)
        total_records += count
        print(f"  Записей: {count}")
        time.sleep(0.2)  # пауза между запросами

    print(f"\nГотово! Всего EAV записей загружено: {total_records}")

if __name__ == "__main__":
    main()
