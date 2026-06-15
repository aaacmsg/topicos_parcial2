import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@st.cache_data
def cargar_datos():
    datasets = {}
    for name in ["imae", "pib_constante", "pib_corriente",
                  "importaciones_valor", "importaciones_peso",
                  "exportaciones", "balanza_pagos", "ipc",
                  "deuda_publica", "ejecucion_presupuestaria", "sociodemograficos"]:
        try:
            datasets[name] = pd.read_parquet(f"data/processed/{name}.parquet")
        except Exception:
            datasets[name] = pd.DataFrame()
    return datasets


def mostrar(datasets):
    st.header("Resumen de Indicadores Economicos")

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    imae = datasets.get("imae")
    if imae is not None and len(imae) > 0:
        ultimo = imae["imae_original"].iloc[-1]
        anterior = imae["imae_original"].iloc[-13] if len(imae) > 13 else imae["imae_original"].iloc[0]
        var = ((ultimo - anterior) / anterior) * 100 if anterior != 0 else 0
        col1.metric("IMAE", f"{ultimo:.1f}", f"{var:+.1f}%")

    pib = datasets.get("pib_constante")
    if pib is not None and len(pib) > 0:
        numeric = pib.select_dtypes(include="number")
        if numeric.shape[1] > 1:
            total = numeric.iloc[-1].sum()
            col2.metric("PIB Trimestral", f"{total:,.0f}M")

    imp_valor = datasets.get("importaciones_valor")
    if imp_valor is not None and len(imp_valor) > 0:
        total_imp = imp_valor.iloc[-1]["bienes_de_consumo"] + imp_valor.iloc[-1]["bienes_intermedios"] + imp_valor.iloc[-1]["bienes_de_capital"]
        col3.metric("Importaciones", f"{total_imp:,.0f}")

    deuda = datasets.get("deuda_publica")
    if deuda is not None and len(deuda) > 0:
        try:
            saldo = deuda.iloc[-1]["saldo"]
            col4.metric("Deuda Publica", f"{saldo:,.2f}")
        except Exception:
            pass

    balanza = datasets.get("balanza_pagos")
    if balanza is not None and len(balanza) > 0:
        col5.metric("Balanza de Pagos", f"{len(balanza)} registros")

    ipc = datasets.get("ipc")
    if ipc is not None and len(ipc) > 0:
        ipc_cols = [c for c in ipc.columns if "total" in c.lower() and c != "fecha"]
        if ipc_cols:
            val = ipc[ipc_cols[0]].iloc[-1]
            col6.metric("IPC", f"{val:.1f}")

    st.divider()
    st.subheader("Indicadores Disponibles")
    for name, df in datasets.items():
        if len(df) > 0:
            cols = [c for c in df.columns if c != "fecha" and not c.endswith("_var_interanual") and not c.endswith("_media_movil_12") and not c.endswith("_lag_")]
            st.write(f"**{name}**: {len(df)} filas, {len(cols)} indicadores")
