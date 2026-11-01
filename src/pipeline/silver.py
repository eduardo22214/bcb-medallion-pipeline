"""SILVER: dado limpo, tipado, deduplicado e validado.

A função `transform` é PURA (entra lista, sai DataFrame): fácil de testar sem rede e sem disco.
"""
import json
import logging
from pathlib import Path

import pandas as pd

from pipeline.bronze import latest_partition_file
from pipeline.config import BRONZE_DIR, SERIES, SILVER_DIR

log = logging.getLogger(__name__)


class DataQualityError(Exception):
    """Levantada quando o dado não passa nas regras de qualidade."""


def transform(records: list[dict], serie: str) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        raise DataQualityError(f"[{serie}] bronze vazio")

    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")  # texto -> data
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")  # texto -> número ("abc" vira NaN)
    df = (
        df.dropna(subset=["data", "valor"])
        .drop_duplicates(subset="data", keep="last")
        .sort_values("data")
        .reset_index(drop=True)
    )
    df["serie"] = serie
    return df[["data", "serie", "valor"]]


def validate(df: pd.DataFrame, serie: str) -> None:
    """Regras de qualidade: falhar cedo é melhor do que propagar dado ruim para a Gold."""
    if df.empty:
        raise DataQualityError(f"[{serie}] sem linhas após limpeza")
    if df["data"].duplicated().any():
        raise DataQualityError(f"[{serie}] datas duplicadas")
    if serie == "dolar" and (df["valor"] <= 0).any():
        raise DataQualityError("[dolar] cotação <= 0")
    if serie == "selic_meta" and not df["valor"].between(0, 100).all():
        raise DataQualityError("[selic_meta] valor fora de 0-100")


def build_silver(serie: str, bronze_dir: Path = BRONZE_DIR, silver_dir: Path = SILVER_DIR) -> Path:
    source = latest_partition_file(serie, bronze_dir)
    records = json.loads(source.read_text(encoding="utf-8"))["records"]

    df = transform(records, serie)
    validate(df, serie)

    target = silver_dir / f"{serie}.parquet"
    target.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(target, index=False)
    log.info("Silver: %d linhas de '%s' -> %s", len(df), serie, target)
    return target


def build_all(**kwargs) -> list[Path]:
    return [build_silver(s, **kwargs) for s in SERIES]
