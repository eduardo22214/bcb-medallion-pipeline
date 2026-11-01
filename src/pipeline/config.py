"""Configurações centrais: caminhos, séries e URL da API."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))

BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

# API SGS do Banco Central: https://dadosabertos.bcb.gov.br
BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"

# nome interno -> código da série no SGS
SERIES = {
    "dolar": 1,        # Dólar americano (venda) - diário
    "selic_meta": 432, # Meta Selic (% a.a.) - diário
    "ipca": 433,       # IPCA variação mensal (%) - mensal
}

START_DATE = "01/01/2020"  # dd/mm/aaaa
