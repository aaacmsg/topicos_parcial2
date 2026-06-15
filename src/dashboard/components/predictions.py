import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.models.prophet_model import predice_imae, entrenar_completo as entrenar_imae
from src.models.arima_model import predice_pib, entrenar_completo as entrenar_pib


def mostrar(datasets):
    st.header("Predicciones")

    modelo_sel = st.selectbox("Selecciona modelo", ["IMAE (Prophet)", "PIB (ARIMA)"])

    if modelo_sel == "IMAE (Prophet)":
        df = datasets.get("imae")
        if df is None or len(df) == 0:
            st.warning("No hay datos IMAE")
            return

        if st.button("Re-entrenar modelo"):
            with st.spinner("Entrenando Prophet..."):
                res = entrenar_imae()
            st.success("Modelo re-entrenado")

        forecast = predice_imae(12)
        historico = df[df["fecha"] < forecast["ds"].iloc[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=historico["fecha"], y=historico["imae_original"],
                                 mode="lines", name="Historico", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"],
                                 mode="lines", name="Prediccion", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_upper"],
                                 mode="lines", name="Limite superior",
                                 line=dict(color="orange", dash="dash"), showlegend=False))
        fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_lower"],
                                 mode="lines", name="Limite inferior",
                                 line=dict(color="orange", dash="dash"),
                                 fill="tonexty", fillcolor="rgba(255,165,0,0.1)", showlegend=False))
        fig.update_layout(title="Prediccion IMAE - 12 meses", xaxis_title="Fecha", yaxis_title="IMAE")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Datos del pronostico")
        f_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        f_df.columns = ["Fecha", "Valor", "Min", "Max"]
        f_df["Fecha"] = f_df["Fecha"].dt.strftime("%Y-%m")
        st.dataframe(f_df, hide_index=True, use_container_width=True)

        csv = f_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar pronostico CSV", csv, "imae_forecast.csv", "text/csv")

    elif modelo_sel == "PIB (ARIMA)":
        df = datasets.get("pib_constante")
        if df is None or len(df) == 0:
            st.warning("No hay datos PIB")
            return

        if st.button("Re-entrenar modelo"):
            with st.spinner("Entrenando ARIMA..."):
                res = entrenar_pib()
            st.success("Modelo re-entrenado")

        forecast = predice_pib(4)
        numeric = df.select_dtypes(include="number")
        if numeric.shape[1] > 1:
            pib_serie = df.iloc[:, 0].astype(str)
            pib_valor = numeric.sum(axis=1)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=pib_serie, y=pib_valor, name="Historico", marker_color="blue"))
            anos_futuros = [f"Pred {i+1}" for i in range(len(forecast))]
            fig.add_trace(go.Bar(x=anos_futuros, y=forecast["mean"], name="Prediccion", marker_color="orange"))
            fig.update_layout(title="Prediccion PIB - 4 trimestres", xaxis_title="Trimestre", yaxis_title="PIB (millones)")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Datos del pronostico")
            f_df = forecast[["mean", "mean_ci_lower", "mean_ci_upper"]].copy()
            f_df.columns = ["Valor", "Min", "Max"]
            st.dataframe(f_df, hide_index=True, use_container_width=True)

            csv = f_df.to_csv(index=False).encode("utf-8")
            st.download_button("Descargar pronostico CSV", csv, "pib_forecast.csv", "text/csv")
