import pandas as pd
import pytest

from pipeline.gold import build_gold


@pytest.fixture
def silver_dir(tmp_path):
    meses = pd.date_range("2023-01-01", periods=12, freq="MS")
    pd.DataFrame({"data": meses, "serie": "dolar", "valor": 5.0}).to_parquet(tmp_path / "dolar.parquet")
    pd.DataFrame({"data": meses, "serie": "selic_meta", "valor": 10.0}).to_parquet(tmp_path / "selic_meta.parquet")
    pd.DataFrame({"data": meses, "serie": "ipca", "valor": 1.0}).to_parquet(tmp_path / "ipca.parquet")
    return tmp_path


def test_ipca_acumulado_12m(silver_dir, tmp_path):
    out = build_gold(silver_dir=silver_dir, gold_dir=tmp_path / "gold")
    df = pd.read_parquet(out)
    assert len(df) == 12
    assert df["ipca_acum_12m"].iloc[:11].isna().all()  # menos de 12 meses: nulo
    assert df["ipca_acum_12m"].iloc[-1] == pytest.approx((1.01**12 - 1) * 100, abs=1e-3)
