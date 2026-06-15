import os
import pickle
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

MODEL_DIR = "data/models"
os.makedirs(MODEL_DIR, exist_ok=True)


def _load_pib():
    df = pd.read_parquet("data/processed/pib_constante.parquet")
    first_col = df.columns[0]
    numeric_cols = df.select_dtypes(include="number").columns
    df["pib_total"] = df[numeric_cols].sum(axis=1)
    result = df[[first_col, "pib_total"]].copy()
    result = result.rename(columns={first_col: "trimestre"})
    result["trimestre"] = result["trimestre"].astype(str).str.strip()
    result = result.sort_values("trimestre").reset_index(drop=True)
    result["fecha"] = pd.to_datetime(result["trimestre"].str.replace("Q1", "-01-01")
                                     .str.replace("Q2", "-04-01")
                                     .str.replace("Q3", "-07-01")
                                     .str.replace("Q4", "-10-01"))
    return result


def entrenar_pib():
    df = _load_pib()
    train = df.iloc[:int(len(df) * 0.8)].copy()
    test = df.iloc[int(len(df) * 0.8):].copy()

    from statsmodels.tsa.statespace.sarimax import SARIMAX

    y_train = train.set_index("fecha")["pib_total"].astype(float)
    y_test = test.set_index("fecha")["pib_total"].astype(float) if len(test) > 0 else pd.Series(dtype=float)

    mejor_modelo = None
    mejor_aic = float("inf")
    for p in range(0, 3):
        for d in range(0, 2):
            for q in range(0, 3):
                try:
                    modelo = SARIMAX(y_train, order=(p, d, q), seasonal_order=(p, d, q, 4),
                                     enforce_stationarity=False, enforce_invertibility=False)
                    res = modelo.fit(disp=False, maxiter=200)
                    if res.aic < mejor_aic:
                        mejor_aic = res.aic
                        mejor_modelo = (p, d, q, res)
                except Exception:
                    continue

    if mejor_modelo is None:
        mejor_modelo = (1, 1, 1, SARIMAX(y_train, order=(1, 1, 1)).fit(disp=False))

    p, d, q, fitted = mejor_modelo
    pred = fitted.get_forecast(steps=4)
    pred_df = pred.summary_frame(alpha=0.2)

    metricas = {}
    if len(y_test) > 2:
        from src.models.evaluator import rmse, mae, mape
        in_sample = fitted.predict(start=len(y_train) - len(y_test), end=len(y_train) - 1)
        metricas = {
            "rmse": rmse(y_test.values, in_sample.values),
            "mae": mae(y_test.values, in_sample.values),
            "mape": mape(y_test.values, in_sample.values),
        }

    ruta = os.path.join(MODEL_DIR, "arima_pib.pkl")
    with open(ruta, "wb") as f:
        pickle.dump(fitted, f)

    return {
        "modelo": fitted,
        "orden": (p, d, q),
        "prediccion": pred_df,
        "metricas": metricas,
        "train": train,
        "test": test,
        "serie": df,
    }


def entrenar_completo():
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    df = _load_pib()
    y = df.set_index("fecha")["pib_total"].astype(float)

    mejor_modelo = None
    mejor_aic = float("inf")
    for p in range(0, 3):
        for d in range(0, 2):
            for q in range(0, 3):
                try:
                    modelo = SARIMAX(y, order=(p, d, q), seasonal_order=(p, d, q, 4),
                                     enforce_stationarity=False, enforce_invertibility=False)
                    res = modelo.fit(disp=False, maxiter=200)
                    if res.aic < mejor_aic:
                        mejor_aic = res.aic
                        mejor_modelo = (p, d, q, res)
                except Exception:
                    continue

    if mejor_modelo is None:
        mejor_modelo = (1, 1, 1, SARIMAX(y, order=(1, 1, 1)).fit(disp=False))

    p, d, q, fitted = mejor_modelo
    pred = fitted.get_forecast(steps=4)
    pred_df = pred.summary_frame(alpha=0.2)

    ruta = os.path.join(MODEL_DIR, "arima_pib.pkl")
    with open(ruta, "wb") as f:
        pickle.dump(fitted, f)

    return {"modelo": fitted, "orden": (p, d, q), "prediccion": pred_df, "serie": df}


def predice_pib(horizon=4):
    ruta = os.path.join(MODEL_DIR, "arima_pib.pkl")
    if not os.path.exists(ruta):
        res = entrenar_completo()
        return res["prediccion"]

    with open(ruta, "rb") as f:
        fitted = pickle.load(f)
    pred = fitted.get_forecast(steps=horizon)
    return pred.summary_frame(alpha=0.2)


if __name__ == "__main__":
    res = entrenar_completo()
    print(f"Orden ARIMA: {res['orden']}")
    print(f"Prediccion 4 trimestres:\n{res['prediccion']}")
