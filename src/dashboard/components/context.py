import streamlit as st
import pandas as pd
import plotly.express as px


def mostrar(datasets):
    st.header("Contexto")

    deuda = datasets.get("deuda_publica")
    if deuda is not None and len(deuda) > 0:
        st.subheader("Deuda Publica")
        numeric = deuda.select_dtypes(include="number")
        if not numeric.empty and "fecha" in deuda.columns:
            deuda_plot = pd.DataFrame({"fecha": deuda["fecha"], "saldo": deuda.iloc[:, 4]})
            fig = px.line(deuda_plot, x="fecha", y="saldo", title="Evolucion de la Deuda Publica")
            st.plotly_chart(fig, use_container_width=True)

    presupuesto = datasets.get("ejecucion_presupuestaria")
    if presupuesto is not None and len(presupuesto) > 0:
        st.subheader("Ejecucion Presupuestaria")
        numeric = presupuesto.select_dtypes(include="number")
        if not numeric.empty:
            total_gasto = numeric.sum(axis=1)
            fig = px.line(y=total_gasto, title="Gasto Total")
            st.plotly_chart(fig, use_container_width=True)

    socio = datasets.get("sociodemograficos")
    if socio is not None and len(socio) > 0:
        st.subheader("Indicadores Sociodemograficos")
        numeric = socio.select_dtypes(include="number")
        if not numeric.empty:
            indicador = st.selectbox("Selecciona indicador", numeric.columns.tolist())
            if len(socio) > 0:
                fig = px.line(socio, x=socio.iloc[:, 0].astype(str), y=socio[indicador],
                              title=f"{indicador}")
                st.plotly_chart(fig, use_container_width=True)
