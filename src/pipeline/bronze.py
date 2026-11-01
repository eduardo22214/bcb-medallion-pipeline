"""BRONZE: dado cru, exatamente como veio da fonte + metadados de ingestão.

Princípios:
- Nunca transformar o dado aqui (se a regra de negócio mudar, reprocessamos a partir do cru).
- Particionar por data de ingestão (ingestion_date=...) para ter histórico e idempotência.
"""
import json
import logging
import time
from datetime import UTC, date, datetime
from pathlib import Path

import requests

from pipeline.config import BCB_URL, BRONZE_DIR, SERIES, START_DATE

log = logging.getLogger(__name__)


def fetch_series(code: int, start: str, end: str, retries: int = 3, timeout: int = 30) -> list[dict]:
    """Chama a API do BCB com retry e backoff exponencial."""
    url = BCB_URL.format(code=code)
    params = {"formato": "json", "dataInicial": start, "dataFinal": end}
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            if attempt == retries:
                raise
            wait = 2**attempt
            log.warning("Falha (%s). Tentativa %d/%d, aguardando %ds", exc, attempt, retries, wait)
            time.sleep(wait)
    return []


def ingest(serie: str, run_date: date | None = None, base_dir: Path = BRONZE_DIR) -> Path:
    """Baixa uma série e grava o JSON cru na partição do dia. Reexecutar sobrescreve a mesma partição."""
    run_date = run_date or date.today()
    code = SERIES[serie]
    start, end = START_DATE, run_date.strftime("%d/%m/%Y")

    records = fetch_series(code, start, end)

    envelope = {
        "metadata": {
            "serie": serie,
            "sgs_code": code,
            "source_url": BCB_URL.format(code=code),
            "period": {"start": start, "end": end},
            "ingested_at": datetime.now(UTC).isoformat(),
            "n_records": len(records),
        },
        "records": records,
    }

    target = base_dir / serie / f"ingestion_date={run_date.isoformat()}" / "data.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(envelope, ensure_ascii=False), encoding="utf-8")
    log.info("Bronze: %s registros de '%s' -> %s", len(records), serie, target)
    return target


def latest_partition_file(serie: str, base_dir: Path = BRONZE_DIR) -> Path:
    """Retorna o arquivo da partição mais recente (usado pela Silver)."""
    files = sorted((base_dir / serie).glob("ingestion_date=*/data.json"))
    if not files:
        raise FileNotFoundError(f"Nenhum dado bronze para '{serie}'. Rode a camada bronze primeiro.")
    return files[-1]
