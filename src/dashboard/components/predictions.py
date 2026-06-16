import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.models.prophet_model import predice_imae, entrenar_completo as entrenar_imae
from src.models.arima_model import predice_pib, entrenar_completo as entrenar_pib


def mostrar(datasets):
    st.markdown(
        "Pronostico de indicadores clave basado en series temporales. "
        "El **IMAE** se modela con Prophet (Meta) usando estacionalidad anual. "
        "El **PIB** se modela con SARIMA (seleccion automatica del mejor orden). "
        "Las bandas de confianza representan el rango estimado al 80%."
    )

    modelo_sel = st.selectbox("Modelo", ["IMAE — Prophet (12 meses)", "PIB — SARIMA (4 trimestres)"])

    if modelo_sel.startswith("IMAE"):
        df = datasets.get("imae")
        if df is None or len(df) == 0:
            st.warning("No hay datos IMAE")
            return

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Re-entrenar modelo"):
                with st.spinner("Entrenando Prophet..."):
                    res = entrenar_imae()
                st.success("Modelo re-entrenado")

        forecast = predice_imae(12)
        historico = df[df["fecha"] < forecast["ds"].iloc[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=historico["fecha"], y=historico["imae_original"],
            mode="lines", name="Historico (2016 - 2026)",
            line=dict(color="#1f77b4", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=forecast["ds"], y=forecast["yhat"],
            mode="lines", name="Pronostico 12 meses",
            line=dict(color="#ff7f0e", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=forecast["ds"], y=forecast["yhat_upper"],
            mode="lines", line=dict(color="#ff7f0e", width=0.5, dash="dash"),
            showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=forecast["ds"], y=forecast["yhat_lower"],
            mode="lines", line=dict(color="#ff7f0e", width=0.5, dash="dash"),
            fill="tonexty", fillcolor="rgba(255,127,14,0.1)",
            name="Intervalo de confianza (80%)",
        ))
        fig.update_layout(
            title="Pronostico del IMAE — Proximo ano",
            xaxis_title="",
            yaxis_title="Indice de Actividad Economica",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tabla del pronostico")
        f_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        f_df.columns = ["Periodo", "Valor estimado", "Minimo (80%)", "Maximo (80%)"]
        f_df["Periodo"] = f_df["Periodo"].dt.strftime("%b %Y")
        f_df["Valor estimado"] = f_df["Valor estimado"].round(1)
        f_df["Minimo (80%)"] = f_df["Minimo (80%)"].round(1)
        f_df["Maximo (80%)"] = f_df["Maximo (80%)"].round(1)
        st.dataframe(f_df, hide_index=True, use_container_width=True)

        csv = f_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", csv, "imae_pronostico.csv", "text/csv")

        with st.expander("Acerca del modelo"):
            st.markdown("""
            **Prophet** es un modelo de series temporales desarrollado por Meta (Facebook).
            Descompone la serie en tendencia, estacionalidad anual y efectos de calendario.
            Se entreno con 121 observaciones mensuales (2016 - 2026) del IMAE del INEC.
            """)

    else:
        df = datasets.get("pib_constante")
        if df is None or len(df) == 0:
            st.warning("No hay datos PIB")
            return

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Re-entrenar modelo"):
                with st.spinner("Entrenando ARIMA..."):
                    res = entrenar_pib()
                st.success("Modelo re-entrenado")

        forecast = predice_pib(4)
        numeric = df.select_dtypes(include="number")
        activity_cols = [c for c in numeric.columns
                         if not any(x in c.lower() for x in ["var_", "media_movil", "lag_", "unnamed"])]
        if len(activity_cols) < 2:
            st.warning("Datos PIB insuficientes")
            return

        raw_dates = df.iloc[:, 0].astype(str)
        fechas_dt = raw_dates.str.replace("Q1", "-01-01").str.replace("Q2", "-04-01")
        fechas_dt = fechas_dt.str.replace("Q3", "-07-01").str.replace("Q4", "-10-01")
        fechas_dt = pd.to_datetime(fechas_dt, errors="coerce")

        pib_valor = numeric[activity_cols].sum(axis=1)
        orden = fechas_dt.argsort()
        fechas_dt = fechas_dt.iloc[orden]
        pib_valor = pib_valor.iloc[orden]
        pib_trimestres = raw_dates.iloc[orden]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pib_trimestres, y=pib_valor,
            mode="lines+markers", name="Historico",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=6),
        ))
        pred_trimestres = [f"Est. {i+1}° trim." for i in range(4)]
        fig.add_trace(go.Scatter(
            x=pred_trimestres, y=forecast["mean"],
            mode="lines+markers", name="Pronostico 4 trimestres",
            line=dict(color="#ff7f0e", width=2, dash="dash"),
            marker=dict(size=8, symbol="diamond"),
        ))
        fig.add_trace(go.Scatter(
            x=pred_trimestres, y=forecast["mean_ci_upper"],
            mode="lines", line=dict(color="#ff7f0e", width=0.5, dash="dash"),
            showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=pred_trimestres, y=forecast["mean_ci_lower"],
            mode="lines", line=dict(color="#ff7f0e", width=0.5, dash="dash"),
            fill="tonexty", fillcolor="rgba(255,127,14,0.1)",
            name="Intervalo de confianza (80%)",
        ))
        fig.update_layout(
            title="Pronostico del PIB Real — Proximos 4 trimestres",
            xaxis_title="",
            yaxis_title="PIB (millones USD)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tabla del pronostico")
        f_df = forecast[["mean", "mean_ci_lower", "mean_ci_upper"]].copy()
        f_df.columns = ["Valor estimado", "Minimo (80%)", "Maximo (80%)"]
        f_df = f_df.round(0).astype(int)
        f_df.index = [f"Trimestre {i+1}" for i in range(4)]
        st.dataframe(f_df, hide_index=False, use_container_width=True)

        csv = f_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", csv, "pib_pronostico.csv", "text/csv")

        with st.expander("Acerca del modelo"):
            st.markdown("""
            **SARIMA** (Seasonal ARIMA) es un modelo estadistico clasico para series temporales.
            El orden optimo se selecciona automaticamente minimizando el AIC (Criterio de Informacion de Akaike).
            Se entreno con datos trimestrales del PIB real del INEC (2018 - 2025).
            """)
