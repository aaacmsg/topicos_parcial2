import pytest
import pandas as pd
import numpy as np
import os
import tempfile

from src.preprocessing.pipeline import (standardize_columns, remove_empty_cols,
    parse_imae_date, parse_anio_mes, unpivot_dataframe, clean_dataset, save_parquet)
from src.preprocessing.features import (variacion_interanual, variacion_mensual,
    media_movil, lag_features, apply_features)


class TestStandardizeColumns:
    def test_basic_renaming(self):
        df = pd.DataFrame({"A\u00f1o de registro": [1], "Tasa (%)": [2]})
        result = standardize_columns(df)
        assert list(result.columns) == ["ano_de_registro", "tasa"]

    def test_accents(self):
        df = pd.DataFrame({"Índice Mensual": [1], "TENDENCIA CICLO": [2]})
        result = standardize_columns(df)
        assert "indice_mensual" in result.columns
        assert "tendencia_ciclo" in result.columns


class TestRemoveEmptyCols:
    def test_removes_unnamed(self):
        df = pd.DataFrame({"a": [1], "Unnamed: 3": [None], "Unnamed: 5": [None]})
        result = remove_empty_cols(df)
        assert list(result.columns) == ["a"]

    def test_keeps_valid(self):
        df = pd.DataFrame({"a": [1], "b": [2]})
        result = remove_empty_cols(df)
        assert list(result.columns) == ["a", "b"]


class TestParseDates:
    def test_imae_date_parsing(self):
        series = pd.Series(["16-ene", "16-feb", "17-mar", "26-dic"])
        result = parse_imae_date(series)
        assert result.iloc[0] == pd.Timestamp("2016-01-01")
        assert result.iloc[1] == pd.Timestamp("2016-02-01")
        assert result.iloc[2] == pd.Timestamp("2017-03-01")
        assert result.iloc[3] == pd.Timestamp("2026-12-01")

    def test_imae_date_na_handling(self):
        series = pd.Series([None, "16-ene"])
        result = parse_imae_date(series)
        assert pd.isna(result.iloc[0])
        assert result.iloc[1] == pd.Timestamp("2016-01-01")

    def test_anio_mes_parsing(self):
        df = pd.DataFrame({"Año": [2020, 2021], "Mes": ["Enero", "Febrero"], "valor": [1, 2]})
        result = parse_anio_mes(df)
        assert "fecha" in result.columns
        assert result["fecha"].iloc[0] == pd.Timestamp("2020-01-01")
        assert result["fecha"].iloc[1] == pd.Timestamp("2021-02-01")


class TestUnpivot:
    def test_basic_unpivot(self):
        df = pd.DataFrame({"pais": ["A", "B"], "2000": [100, 200], "2001": [150, 250]})
        config = {"id_vars": ["pais"], "var_name": "año", "value_name": "valor"}
        result = unpivot_dataframe(df, config)
        assert result.shape[0] == 4
        assert "año" in result.columns
        assert "valor" in result.columns


class TestFeatures:
    def test_variacion_interanual(self):
        df = pd.DataFrame({"valor": [100, 100, 100, 100, 110, 110]})
        df, col = variacion_interanual(df, "valor", period=4)
        assert pd.isna(df[col].iloc[3])
        assert df[col].iloc[4] == pytest.approx(10.0)

    def test_variacion_mensual(self):
        df = pd.DataFrame({"valor": [100, 105, 110]})
        df, col = variacion_mensual(df, "valor")
        assert pd.isna(df[col].iloc[0])
        assert df[col].iloc[1] == pytest.approx(5.0)

    def test_media_movil(self):
        df = pd.DataFrame({"valor": [1, 2, 3, 4, 5]})
        df, col = media_movil(df, "valor", window=3)
        assert df[col].iloc[2] == pytest.approx(2.0)
        assert df[col].iloc[4] == pytest.approx(4.0)

    def test_lag_features(self):
        df = pd.DataFrame({"valor": [1, 2, 3, 4]})
        result = lag_features(df, "valor", lags=[1, 2])
        assert "valor_lag_1" in result.columns
        assert "valor_lag_2" in result.columns
        assert result["valor_lag_1"].iloc[1] == 1


class TestPipeline:
    def test_clean_dataset_imae(self):
        filepath = "data/raw/imae.csv"
        if not os.path.exists(filepath):
            pytest.skip("imae.csv not found")
        df = clean_dataset(filepath, "imae")
        assert "fecha" in df.columns
        assert "datetime64" in str(df["fecha"].dtype)
        assert df.shape[1] >= 2

    def test_clean_dataset_importaciones(self):
        filepath = "data/raw/importaciones_valor.csv"
        if not os.path.exists(filepath):
            pytest.skip("importaciones_valor.csv not found")
        df = clean_dataset(filepath, "importaciones_valor")
        assert "fecha" in df.columns
        assert df.shape[1] >= 4

    def test_clean_dataset_exportaciones(self):
        filepath = "data/raw/exportaciones.csv"
        if not os.path.exists(filepath):
            pytest.skip("exportaciones.csv not found")
        df = clean_dataset(filepath, "exportaciones")
        assert "pais_de_destino" in df.columns
        assert "a\u00f1o" in df.columns or "ano" in df.columns
        assert "valor_exportacion" in df.columns

    def test_clean_dataset_balanza(self):
        filepath = "data/raw/balanza_pagos.csv"
        if not os.path.exists(filepath):
            pytest.skip("balanza_pagos.csv not found")
        df = clean_dataset(filepath, "balanza_pagos")
        assert df.shape[1] >= 3, f"Solo {df.shape[1]} columnas: {list(df.columns)}"

    def test_clean_dataset_deuda(self):
        filepath = "data/raw/deuda_publica.csv"
        if not os.path.exists(filepath):
            pytest.skip("deuda_publica.csv not found")
        df = clean_dataset(filepath, "deuda_publica")
        assert df.shape[1] >= 3, f"Solo {df.shape[1]} columnas: {list(df.columns)[:5]}"

    def test_save_parquet(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with tempfile.TemporaryDirectory() as tmp:
            path = save_parquet(df, "test", tmp)
            loaded = pd.read_parquet(path)
            assert loaded.shape == (2, 2)
