"""CLI para rodar o pipeline sem Airflow:  python -m pipeline.run --layer all"""
import argparse
import logging

from pipeline import bronze, gold, silver
from pipeline.config import SERIES


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Pipeline medalhão - indicadores BCB")
    parser.add_argument("--layer", choices=["bronze", "silver", "gold", "all"], default="all")
    args = parser.parse_args()

    if args.layer in ("bronze", "all"):
        for serie in SERIES:
            bronze.ingest(serie)
    if args.layer in ("silver", "all"):
        silver.build_all()
    if args.layer in ("gold", "all"):
        gold.build_gold()


if __name__ == "__main__":
    main()
