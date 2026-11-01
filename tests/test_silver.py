import pytest

from pipeline.silver import DataQualityError, transform, validate


def test_transform_converte_tipos_e_remove_duplicatas():
    records = [
        {"data": "02/01/2024", "valor": "4.90"},
        {"data": "02/01/2024", "valor": "4.91"},  # duplicada: fica a última
        {"data": "03/01/2024", "valor": "abc"},   # inválida: descartada
        {"data": "01/01/2024", "valor": "4.85"},
    ]
    df = transform(records, "dolar")
    assert list(df["valor"]) == [4.85, 4.91]
    assert df["data"].is_monotonic_increasing
    assert set(df.columns) == {"data", "serie", "valor"}


def test_bronze_vazio_falha():
    with pytest.raises(DataQualityError):
        transform([], "dolar")


def test_dolar_negativo_falha_na_validacao():
    df = transform([{"data": "01/01/2024", "valor": "-1"}], "dolar")
    with pytest.raises(DataQualityError):
        validate(df, "dolar")
