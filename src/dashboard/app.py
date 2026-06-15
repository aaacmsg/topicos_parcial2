import streamlit as st
from src.dashboard.components import overview, trends, predictions, trade, context

st.set_page_config(page_title="Indicadores Economicos Panama", layout="wide")

st.title("Dashboard de Indicadores Economicos de Panama")
st.caption("Fuente: datosabiertos.gob.pa (CKAN API)")

datasets = overview.cargar_datos()

paginas = {
    "Resumen": overview.mostrar,
    "Tendencias": trends.mostrar,
    "Predicciones": predictions.mostrar,
    "Comercio Exterior": trade.mostrar,
    "Contexto": context.mostrar,
}

seleccion = st.sidebar.radio("Navegacion", list(paginas.keys()))
paginas[seleccion](datasets)

st.sidebar.divider()
st.sidebar.caption("Proyecto Gestion de la Informacion")
st.sidebar.caption("Tema 2: Indicadores Economicos de Panama")
st.sidebar.caption("II Semestre 2026")
