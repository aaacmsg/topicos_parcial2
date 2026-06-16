import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.data_utils import get_deuda_mensual


def _labels_espanol(col_name):
    labels = {
        "densidad_de_la_poblacion": "Densidad poblacional (hab/km2)",
        "tasa_bruta_de_natalidad": "Tasa bruta de natalidad",
        "tasa_global_de_fecundidad": "Tasa global de fecundidad",
        "tasa_bruta_de_mortalidad": "Tasa bruta de mortalidad",
        "tasa_de_mortalidad_infantil": "Tasa de mortalidad infantil",
        "esperanza_de_vida_al_nacer": "Esperanza de vida al nacer (anos)",
        "relacion_de_alumnos_por_docente_en_educacion_primaria": "Alumnos por docente (primaria)",
        "tasa_de_desercion_de_educacion_primaria_3": "Tasa de desercion escolar (%)",
        "poblacion": "Poblacion total",
        "habitantes_por_medicos": "Habitantes por medico",
    }
    return labels.get(col_name, col_name.replace("_", " ").title())


def mostrar(datasets):
    st.markdown(
        "Indicadores complementarios: deuda del sector publico (**MEF**), "
        "ejecucion presupuestaria del gobierno (**Contraloria General**) e "
        "indicadores sociodemograficos (**INEC**)."
    )

    deuda = datasets.get("deuda_publica")
    presupuesto = datasets.get("ejecucion_presupuestaria")
    socio = datasets.get("sociodemograficos")

    tabs = st.tabs(["Deuda Publica", "Ejecucion Presupuestaria", "Sociodemograficos"])

    with tabs[0]:
        if deuda is not None and len(deuda) > 1:
            st.subheader("Evolucion de la Deuda Publica — MEF")
            fechas, saldo = get_deuda_mensual(deuda)
            if fechas is not None and len(saldo) > 0:
                fig = px.line(
                    x=fechas, y=saldo,
                    title="Saldo de deuda del sector publico",
                    labels={"x": "", "y": "Saldo (millones USD)"},
                )
                fig.update_traces(line=dict(width=2, color="#1f77b4"))
                st.plotly_chart(fig, use_container_width=True)

                st.metric("Ultimo saldo registrado", f"${saldo.iloc[-1]:,.2f}M")
                st.caption(f"Ultimo dato: {fechas.iloc[-1].strftime('%b %Y')}")
        else:
            st.warning("No hay datos de deuda publica")

        with st.expander("Fuente"):
            st.markdown("**Ministerio de Economia y Finanzas (MEF)** — Reportes de deuda publica. Datos via datosabiertos.gob.pa.")

    with tabs[1]:
        if presupuesto is not None and len(presupuesto) > 0:
            st.subheader("Ejecucion Presupuestaria — Contraloria General")
            numeric = presupuesto.select_dtypes(include="number")
            if not numeric.empty:
                total = numeric.sum(axis=1)
                if len(total) > 0:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=total.values, mode="lines+markers",
                        name="Gasto total", line=dict(width=2, color="#2ca02c"),
                    ))
                    fig.update_layout(
                        title="Ejecucion presupuestaria de gastos",
                        xaxis_title="Registro",
                        yaxis_title="Monto (USD)",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    ult_gasto = total.iloc[-1]
                    st.metric("Ultimo registro de gasto", f"${ult_gasto:,.0f}")
        else:
            st.warning("No hay datos de ejecucion presupuestaria")

        with st.expander("Fuente"):
            st.markdown("**Contraloria General de la Republica** — Ejecucion presupuestaria de gastos del gobierno central. Datos via datosabiertos.gob.pa.")

    with tabs[2]:
        if socio is not None and len(socio) > 0:
            st.subheader("Indicadores Sociodemograficos — INEC")
            st.caption(f"Datos anuales de {socio.iloc[:, 0].min()} a {socio.iloc[:, 0].max()} ({len(socio)} anos)")
            numeric = socio.select_dtypes(include="number")
            indicadores = [c for c in numeric.columns if c.lower().strip() not in ("ano", "a\u00f1o", "año")]
            if indicadores:
                opciones = {_labels_espanol(c): c for c in indicadores}
                label_sel = st.selectbox("Selecciona indicador", list(opciones.keys()))
                col_name = opciones[label_sel]

                if len(socio) > 0:
                    x_col = socio.columns[0]
                    df_plot = socio[[x_col, col_name]].dropna().copy()
                    df_plot[x_col] = df_plot[x_col].astype(str)

                    fig = px.line(
                        df_plot, x=x_col, y=col_name,
                        title=label_sel,
                        labels={x_col: "A\u00f1o", col_name: label_sel},
                        markers=True,
                    )
                    fig.update_traces(line=dict(width=2), marker=dict(size=8))
                    fig.update_layout(xaxis=dict(type="category"))
                    st.plotly_chart(fig, use_container_width=True)

                    ult_val = socio[col_name].dropna().iloc[-1]
                    ult_anio = str(socio[x_col].dropna().iloc[-1])
                    st.metric(f"Ultimo ({ult_anio}): {label_sel}", f"{ult_val:.2f}")

                    with st.expander("Ver tabla completa"):
                        st.dataframe(socio, hide_index=True, use_container_width=True)
        else:
            st.warning("No hay datos sociodemograficos")

        with st.expander("Fuente"):
            st.markdown("**INEC** — Indicadores sociodemograficos de Panama. Incluye densidad poblacional, tasas de natalidad, mortalidad, esperanza de vida, educacion y salud. Datos via datosabiertos.gob.pa.")
