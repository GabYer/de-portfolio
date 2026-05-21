from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "gabyer",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
        dag_id="de_portfolio_ingestion",
        default_args=default_args,
        description="Ingestion pipeline: 7 sources → Neon DWH + ClickHouse",
        schedule="0 */6 * * *",
        start_date=datetime(2026, 5, 18),
        catchup=False,
        tags=["portfolio", "ingestion"],
) as dag:

    git_pull = BashOperator(
        task_id="git_pull",
        bash_command="""
            set -e
            sudo chown -R gabyer:gabyer /data/de-portfolio
            cd /data/de-portfolio
            git reset --hard origin/main
            git pull origin main
        """,
    )

    ingest = BashOperator(
        task_id="ingest_all_sources",
        bash_command="""
            set -e
            cd /data/de-portfolio/ingestion
            python run_all.py
        """,
    )

    binance = BashOperator(
        task_id="binance_realtime",
        bash_command="""
            set -e
            cd /data/de-portfolio/ingestion
            python sources/binance_consumer.py
        """,
    )

    transform = BashOperator(
        task_id="staging_transform",
        bash_command="""
            set -e
            docker run --rm \
                -v /data/de-portfolio/dbt:/dbt \
                --env-file /data/de-portfolio/.env \
                dbt-dbt:latest \
                dbt run --project-dir /dbt --profiles-dir /dbt
        """,
    )

    git_pull >> ingest >> binance >> transform