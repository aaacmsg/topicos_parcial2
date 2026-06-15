import os
import pickle
import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json

MODEL_DIR = "data/models"
os.makedirs(MODEL_DIR, exist_ok=True)


def _load_imae():
    df = pd.read_parquet("data/processed/imae.parquet")
    df = df[["fecha", "imae_original"]].dropna().copy()
    df = df.rename(columns={"fecha": "ds", "imae_original": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.sort_values("ds").reset_index(drop=True)
    return df


def entrenar_imae(cambiar_punto=None):
    df = _load_imae()
    train = df.iloc[:int(len(df) * 0.8)]
    test = df.iloc[int(len(df) * 0.8):]

    modelo = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    if cambiar_punto:
        for p in cambiar_punto:
            modelo.add_changepoint(p)
    modelo.fit(train)

    futuro = modelo.make_future_dataframe(periods=12, freq="ME")
    pred = modelo.predict(futuro)

    pred_test = pred.iloc[-len(test) - 12:-12] if len(test) > 0 else pred.iloc[-12:]
    y_true = test["y"].values[:len(pred_test)]
    y_pred = pred_test["yhat"].values[:len(y_true)]

    metricas = {}
    if len(y_true) > 2:
        from src.models.evaluator import rmse, mae, mape
        metricas = {
            "rmse": rmse(y_true, y_pred),
            "mae": mae(y_true, y_pred),
            "mape": mape(y_true, y_pred),
        }

    ruta = os.path.join(MODEL_DIR, "prophet_imae.json")
    with open(ruta, "w") as f:
        f.write(model_to_json(modelo))

    return {"modelo": modelo, "prediccion": pred, "metricas": metricas, "train": train, "test": test}


def entrenar_completo():
    df = _load_imae()
    modelo = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    modelo.fit(df)
    futuro = modelo.make_future_dataframe(periods=12, freq="ME")
    pred = modelo.predict(futuro)

    ruta = os.path.join(MODEL_DIR, "prophet_imae.json")
    with open(ruta, "w") as f:
        f.write(model_to_json(modelo))

    return {"modelo": modelo, "prediccion": pred, "serie": df}


def predice_imae(horizon=12):
    ruta = os.path.join(MODEL_DIR, "prophet_imae.json")
    if not os.path.exists(ruta):
        res = entrenar_completo()
        return res["prediccion"][["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon + 12)

    with open(ruta) as f:
        modelo = model_from_json(f.read())

    futuro = modelo.make_future_dataframe(periods=horizon, freq="ME")
    pred = modelo.predict(futuro)
    return pred[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon)


if __name__ == "__main__":
    res = entrenar_completo()
    print(res["prediccion"][["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(12))


if __name__ == "__main__":
    res = entrenar_imae()
    print(f"Metricas: {res['metricas']}")
    print(res["prediccion"][["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(12))
