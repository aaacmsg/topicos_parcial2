"""
Funciones de feature engineering para series temporales economicas.
"""

import pandas as pd


def variacion_interanual(df, col, period=12):
    """Variacion porcentual respecto al mismo periodo del ano anterior."""
    new_col = f"{col}_var_interanual"
    df[new_col] = ((df[col] - df[col].shift(period)) / df[col].shift(period)) * 100
    return df, new_col


def variacion_mensual(df, col, period=1):
    """Variacion porcentual respecto al mes anterior."""
    new_col = f"{col}_var_mensual"
    df[new_col] = ((df[col] - df[col].shift(period)) / df[col].shift(period)) * 100
    return df, new_col


def media_movil(df, col, window=12):
    """Media movil simple."""
    new_col = f"{col}_media_movil_{window}"
    df[new_col] = df[col].rolling(window=window, min_periods=1).mean()
    return df, new_col


def lag_features(df, col, lags=None):
    """Rezagos de la serie."""
    if lags is None:
        lags = [1, 2, 4, 12]
    for lag in lags:
        new_col = f"{col}_lag_{lag}"
        df[new_col] = df[col].shift(lag)
    return df


def apply_features(df, col, feature_list):
    """Aplica lista de features sobre una columna."""
    for feat in feature_list:
        if feat == "variacion_interanual":
            df, _ = variacion_interanual(df, col)
        elif feat == "variacion_mensual":
            df, _ = variacion_mensual(df, col)
        elif feat.startswith("media_movil_"):
            window = int(feat.split("_")[-1])
            df, _ = media_movil(df, col, window)
        elif feat == "lag_features":
            df = lag_features(df, col)
    return df
