"""DAG de orquestração: bronze (1 task por série) -> silver (1 task por série) -> gold."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task

from pipeline.config import SERIES


@dag(
    dag_id="medallion_bcb",
    description="Pipeline medalhão com indicadores econômicos do Banco Central",
    schedule="0 8 * * 1-5",  # dias úteis às 08:00
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["medallion", "bcb", "portfolio"],
)
def medallion_bcb():
    @task
    def bronze(serie: str) -> str:
        from pipeline.bronze import ingest

        ingest(serie)
        return serie  # devolve o nome para encadear a silver da MESMA série

    @task
    def silver(serie: str) -> str:
        from pipeline.silver import build_silver

        return str(build_silver(serie))

    @task
    def gold() -> str:
        from pipeline.gold import build_gold

        return str(build_gold())

    # Dynamic Task Mapping: cria uma task por série em tempo de execução
    bronze_runs = bronze.expand(serie=list(SERIES))
    silver_runs = silver.expand(serie=bronze_runs)
    silver_runs >> gold()


medallion_bcb()
