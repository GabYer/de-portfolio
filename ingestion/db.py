import os
import psycopg2
from psycopg2.extras import execute_values

def get_connection():
    url = os.environ["DATABASE_URL"]
    return psycopg2.connect(url, connect_timeout=10)

def bulk_insert(conn, table, rows, columns):
    if not rows:
        return 0
    cols = ", ".join(columns)
    sql = f"INSERT INTO {table} ({cols}) VALUES %s ON CONFLICT DO NOTHING"
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=500)
    conn.commit()
    return len(rows)

def log_run(conn, name, status, rows=0, error=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO meta.pipeline_runs
                (pipeline_name, source, status, rows_loaded, error_message, started_at, finished_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """, (name, name, status, rows, error))
    conn.commit()
