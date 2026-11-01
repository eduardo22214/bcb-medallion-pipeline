"""GOLD: tabela analítica pronta para consumo (BI, dashboards, análises).

Regra de negócio mora aqui: agregação mensal, variação do dólar e IPCA acumulado em 12 meses.
Usamos SQL no DuckDB, que lê Parquet direto, sem servidor de banco.
"""
import logging
from pathlib import Path

import duckdb

from pipeline.config import GOLD_DIR, SILVER_DIR

log = logging.getLogger(__name__)

GOLD_SQL = """
WITH dolar AS (
    SELECT CAST(date_trunc('month', data) AS DATE) AS mes,
           avg(valor) AS dolar_medio
    FROM read_parquet('{silver}/dolar.parquet')
    GROUP BY 1
),
selic AS (
    SELECT CAST(date_trunc('month', data) AS DATE) AS mes,
           arg_max(valor, data) AS selic_meta_fim_mes   -- último valor do mês
    FROM read_parquet('{silver}/selic_meta.parquet')
    GROUP BY 1
),
ipca AS (
    SELECT CAST(date_trunc('month', data) AS DATE) AS mes,
           valor AS ipca_mensal
    FROM read_parquet('{silver}/ipca.parquet')
),
base AS (
    SELECT d.mes, d.dolar_medio, s.selic_meta_fim_mes, i.ipca_mensal
    FROM dolar d
    LEFT JOIN selic s USING (mes)
    LEFT JOIN ipca  i USING (mes)
)
SELECT
    mes,
    round(dolar_medio, 4)                                         AS dolar_medio,
    round(dolar_medio / lag(dolar_medio) OVER w - 1, 4)           AS dolar_var_mensal,
    selic_meta_fim_mes,
    ipca_mensal,
    CASE WHEN count(ipca_mensal) OVER j = 12
         THEN round((exp(sum(ln(1 + ipca_mensal / 100)) OVER j) - 1) * 100, 4)
    END                                                           AS ipca_acum_12m
FROM base
WINDOW w AS (ORDER BY mes),
       j AS (ORDER BY mes ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
ORDER BY mes
"""


def build_gold(silver_dir: Path = SILVER_DIR, gold_dir: Path = GOLD_DIR) -> Path:
    gold_dir.mkdir(parents=True, exist_ok=True)
    target = gold_dir / "indicadores_mensais.parquet"
    query = GOLD_SQL.format(silver=silver_dir.as_posix())

    con = duckdb.connect()
    con.execute(f"COPY ({query}) TO '{target.as_posix()}' (FORMAT PARQUET)")
    n = con.execute(f"SELECT count(*) FROM read_parquet('{target.as_posix()}')").fetchone()[0]
    con.close()

    if n == 0:
        raise ValueError("Gold gerada vazia")
    log.info("Gold: %d meses -> %s", n, target)
    return target
