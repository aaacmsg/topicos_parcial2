"""
Pipeline de preprocesamiento: limpia CSVs crudos y genera Parquets limpios.
Soporta separadores, encodings, parseo de fechas, unpivot, y feature engineering.
"""

import os
import re
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing.datasets_prep_config import PREP_CONFIG
from src.preprocessing.features import apply_features


def _clean_col_name(col):
    """Limpia un nombre de columna individual."""
    if not isinstance(col, str):
        return str(col).strip()
    new = col.strip()
    new = new.replace("\ufeff", "").replace("\ufed3", "")
    new = new.lower()
    new = new.replace(" ", "_")
    new = new.replace("/", "_")
    new = new.replace("-", "_")
    new = new.replace("(", "").replace(")", "").replace("%", "")
    new = new.replace(".", "_")
    for acc, simp in [("\u00e1", "a"), ("\u00e9", "e"), ("\u00ed", "i"), ("\u00f3", "o"), ("\u00fa", "u"),
                       ("\u00f1", "n"), ("\u00e3", "a"), ("\u00e7", "c"), ("\u00e2", "a"), ("\u00ea", "e"),
                       ("\u00f4", "o"), ("\u00f5", "o"), ("\u00fc", "u"), ("\u00e4", "a"), ("\u00f6", "o")]:
        new = new.replace(acc, simp)
    new = re.sub(r"_+", "_", new).strip("_")
    return new


def standardize_columns(df):
    """Normaliza nombres de columnas: minusculas, sin acentos, _ por espacios."""
    rename = {col: _clean_col_name(col) for col in df.columns}
    return df.rename(columns=rename)


def remove_empty_cols(df):
    """Descarta columnas totalmente vacias o Unnamed."""
    if df.columns.dtype == "object":
        unnamed_mask = df.columns.str.contains("^unnamed", case=False, na=False)
        df = df.loc[:, ~unnamed_mask]
    df = df.dropna(axis=1, how="all")
    return df


def parse_imae_date(series):
    """Convierte formato '16-ene' a datetime."""
    mes_map = {
        "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
        "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
    }
    def parse(val):
        if pd.isna(val):
            return pd.NaT
        val = str(val).strip().lower()
        parts = val.split("-")
        if len(parts) != 2:
            return pd.NaT
        try:
            anio = int(parts[0]) + 2000 if int(parts[0]) < 100 else int(parts[0])
            mes = mes_map.get(parts[1], 1)
            return pd.Timestamp(year=anio, month=mes, day=1)
        except (ValueError, KeyError):
            return pd.NaT
    return series.apply(parse)


def parse_anio_mes(df):
    """Convierte columnas Año + Mes a una columna fecha datetime."""
    mes_map = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
        "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
        "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
    }
    anio_col = None
    mes_col = None
    for c in df.columns:
        cl = c.lower().strip()
        if cl in ("año", "ano", "aã±o", "aãƒâ±o", "year"):
            anio_col = c
        elif cl in ("mes", "month"):
            mes_col = c

    if anio_col is None or mes_col is None:
        return df

    def to_int(val):
        try:
            return int(float(str(val).strip()))
        except (ValueError, TypeError):
            return None

    def get_mes(val):
        val = str(val).strip().lower()
        if val.isdigit():
            return int(val)
        return mes_map.get(val, 1)

    fechas = []
    for _, row in df.iterrows():
        anio = to_int(row[anio_col])
        mes = get_mes(row[mes_col])
        if anio and mes:
            fechas.append(pd.Timestamp(year=anio, month=mes, day=1))
        else:
            fechas.append(pd.NaT)
    df["fecha"] = fechas
    return df


def split_single_column(df, delimiter=";"):
    """Si el DataFrame tiene 1 columna con valores separados, los divide."""
    if df.shape[1] == 1:
        col_name = df.columns[0]
        col_str = str(col_name)
        if delimiter in col_str:
            parts = col_str.split(delimiter)
            new_names = [p.strip().replace("\ufeff", "").replace("\ufed3", "") for p in parts]
            df = df[col_name].str.split(delimiter, expand=True)
            if len(new_names) == df.shape[1]:
                df.columns = new_names
            return df
        df = df[col_name].str.split(delimiter, expand=True)
    return df


def unpivot_dataframe(df, config):
    """Convierte formato ancho a largo."""
    if not config:
        return df
    id_vars = config.get("id_vars", [])
    var_name = config.get("var_name", "variable")
    value_name = config.get("value_name", "valor")

    existing_id_vars = [c for c in id_vars if c in df.columns]
    if not existing_id_vars:
        return df
    value_vars = [c for c in df.columns if c not in existing_id_vars]
    if not value_vars:
        return df
    df = df.melt(id_vars=existing_id_vars, value_vars=value_vars,
                 var_name=var_name, value_name=value_name)
    df = df.dropna(subset=[value_name])
    return df


def clean_dataset(filepath, name):
    """Limpia un dataset segun su configuracion y retorna DataFrame limpio."""
    config = PREP_CONFIG.get(name)
    if config is None:
        return pd.read_csv(filepath)

    skip_rows = config.get("skip_rows", 0)

    for enc in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(filepath, encoding=enc, skiprows=skip_rows, low_memory=False)
            break
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    else:
        df = pd.read_csv(filepath, encoding="utf-8", skiprows=skip_rows, low_memory=False, encoding_errors="replace")

    if config.get("reparse_semicolon"):
        with open(filepath, encoding="utf-8-sig") as f:
            raw_text = f.read()
        import io
        df = pd.read_csv(io.StringIO(raw_text), sep=";", skiprows=skip_rows, low_memory=False)

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.replace("\ufeff", "", regex=False)
            df[col] = df[col].str.replace("\ufed3", "", regex=False)
            df[col] = df[col].str.strip()

    df.columns = [c.replace("\ufeff", "").replace("\ufed3", "") if isinstance(c, str) else c for c in df.columns]

    rename = config.get("rename_cols", {})
    if rename:
        rename_actual = {k: v for k, v in rename.items() if k in df.columns}
        if rename_actual:
            df = df.rename(columns=rename_actual)

    df = remove_empty_cols(df)
    df = standardize_columns(df)

    drop_cols = config.get("drop_cols", [])
    if drop_cols:
        drop_actual = [c for c in drop_cols if c in df.columns]
        if drop_actual:
            df = df.drop(columns=drop_actual, errors="ignore")

    unpivot_cfg = config.get("unpivot")
    if unpivot_cfg:
        df = unpivot_dataframe(df, unpivot_cfg)

    date_parser = config.get("date_parser")
    if date_parser == "imae":
        if "fecha" in df.columns:
            df["fecha"] = parse_imae_date(df["fecha"])
    elif date_parser == "anio_mes":
        df = parse_anio_mes(df)

    date_cols = config.get("date_cols")
    if date_cols and date_parser != "anio_mes" and date_parser != "imae":
        for c in date_cols:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")

    feature_eng = config.get("feature_eng", [])
    if feature_eng:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:1]:
            df = apply_features(df, col, feature_eng)

    df = df.sort_values(by=["fecha"]) if "fecha" in df.columns else df
    df = df.reset_index(drop=True)
    return df


def save_parquet(df, name, path=None):
    """Guarda DataFrame como Parquet."""
    if path is None:
        path = os.path.join(ROOT, "data", "processed")
    os.makedirs(path, exist_ok=True)
    filepath = os.path.join(path, f"{name}.parquet")
    df.to_parquet(filepath, index=False)
    return filepath


def run_pipeline(configs=None):
    """Ejecuta pipeline sobre todos los datasets configurados."""
    if configs is None:
        configs = PREP_CONFIG
    results = {}
    for name in configs:
        filepath = os.path.join(ROOT, "data", "raw", f"{name}.csv")
        if not os.path.exists(filepath):
            print(f"  [SKIP] {name}: no existe {filepath}")
            results[name] = None
            continue
        try:
            df = clean_dataset(filepath, name)
            out = save_parquet(df, name)
            print(f"  [OK] {name}: {df.shape[0]} filas x {df.shape[1]} cols -> {out}")
            results[name] = df
        except Exception as e:
            print(f"  [ERR] {name}: {e}")
            results[name] = None
    return results
