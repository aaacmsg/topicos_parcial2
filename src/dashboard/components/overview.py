import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.dashboard.data_utils import get_deuda_mensual

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(ROOT, "data", "processed")

META = {
    "imae": {"nombre": "IMAE", "desc": "Indice Mensual de Actividad Economica", "fuente": "INEC", "unidad": "indice"},
    "pib_constante": {"nombre": "PIB Real", "desc": "Producto Interno Bruto (precios constantes)", "fuente": "INEC", "unidad": "millones USD"},
    "importaciones_valor": {"nombre": "Importaciones", "desc": "Valor CIF de importaciones", "fuente": "INEC", "unidad": "USD"},
    "deuda_publica": {"nombre": "Deuda Publica", "desc": "Saldo de deuda del sector publico", "fuente": "MEF", "unidad": "millones USD"},
    "balanza_pagos": {"nombre": "Balanza de Pagos", "desc": "Cuenta corriente de balanza de pagos", "fuente": "INEC", "unidad": "millones USD"},
    "ipc": {"nombre": "IPC", "desc": "Indice de Precios al Consumidor", "fuente": "INEC", "unidad": "indice"},
}


@st.cache_data
def cargar_datos():
    datasets = {}
    for name in ["imae", "pib_constante", "pib_corriente",
                  "importaciones_valor", "importaciones_peso",
                  "exportaciones", "balanza_pagos", "ipc",
                  "deuda_publica", "ejecucion_presupuestaria", "sociodemograficos"]:
        path = os.path.join(DATA_DIR, f"{name}.parquet")
        try:
            datasets[name] = pd.read_parquet(path)
        except Exception:
            datasets[name] = pd.DataFrame()
    return datasets


def _formatear(valor, unidad):
    if pd.isna(valor) or valor == 0:
        return "N/D", ""
    if unidad == "millones USD":
        return f"${valor:,.2f}M", f"{valor:,.2f}"
    if unidad == "USD":
        if abs(valor) >= 1e9:
            return f"${valor/1e9:.2f}MM", f"{valor:,.0f}"
        if abs(valor) >= 1e6:
            return f"${valor/1e6:.2f}M", f"{valor:,.0f}"
        return f"${valor:,.0f}", f"{valor:,.0f}"
    return f"{valor:,.1f}", f"{valor:,.1f}"


def _sparkline(series, height=60):
    if series is None or len(series) < 2:
        return None
    series = series.dropna().tail(24)
    if len(series) < 2:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=series.values, mode="lines",
        line=dict(width=2, color="#1f77b4"),
        showlegend=False
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def _tarjeta(datasets, name, col):
    df = datasets.get(name)
    if df is None or len(df) == 0:
        col.metric(META[name]["nombre"], "Sin datos")
        return

    meta = META.get(name, {"nombre": name, "fuente": "", "unidad": ""})
    fecha_str = "-"
    var_str = ""

    if name == "imae":
        serie = df["imae_original"].dropna()
        ultimo = serie.iloc[-1]
        anterior = serie.iloc[-13] if len(serie) > 13 else serie.iloc[0]
        var = ((ultimo - anterior) / anterior) * 100 if anterior else 0
        var_str = f"{'+' if var > 0 else ''}{var:.1f}% anual"
        if "fecha" in df.columns:
            fecha_str = pd.to_datetime(df["fecha"].iloc[-1]).strftime("%b %Y")
        valor_str, _ = _formatear(ultimo, meta["unidad"])
        col.metric(f"{meta['nombre']} — {meta['fuente']}", valor_str, var_str)

    elif name == "pib_constante":
        numeric = df.select_dtypes(include="number")
        if numeric.shape[1] > 1:
            serie = numeric.sum(axis=1)
            ultimo = serie.iloc[-1]
            ant = serie.iloc[-5] if len(serie) > 5 else serie.iloc[0]
            var = ((ultimo - ant) / ant) * 100 if ant else 0
            var_str = f"{'+' if var > 0 else ''}{var:.1f}% anual"
            fecha_str = str(df.iloc[-1, 0]) if not numeric.empty else "-"
            valor_str, _ = _formatear(ultimo, meta["unidad"])
            col.metric(f"{meta['nombre']} — {meta['fuente']}", valor_str, var_str)

    elif name == "importaciones_valor":
        cols_bienes = [c for c in df.columns if c.startswith("bienes_")]
        if cols_bienes:
            serie = df[cols_bienes].sum(axis=1)
            ultimo = serie.iloc[-1]
            ant = serie.iloc[-13] if len(serie) > 13 else serie.iloc[0]
            var = ((ultimo - ant) / ant) * 100 if ant else 0
            var_str = f"{'+' if var > 0 else ''}{var:.1f}% anual"
            if "fecha" in df.columns:
                fecha_str = pd.to_datetime(df["fecha"].iloc[-1]).strftime("%b %Y")
            valor_str, _ = _formatear(ultimo, meta["unidad"])
            col.metric(f"{meta['nombre']} — {meta['fuente']}", valor_str, var_str)

    elif name == "deuda_publica":
        fechas, serie = get_deuda_mensual(df)
        if fechas is not None and len(serie) > 0:
            ultimo = serie.iloc[-1]
            ant = serie.iloc[-2] if len(serie) > 1 else serie.iloc[0]
            var = ((ultimo - ant) / ant) * 100 if ant else 0
            var_str = f"{'+' if var > 0 else ''}{var:.1f}% mensual"
            fecha_str = fechas.iloc[-1].strftime("%b %Y")
            valor_str, _ = _formatear(ultimo, "millones USD")
            col.metric(f"{meta['nombre']} — {meta['fuente']}", valor_str, var_str)

    elif name == "balanza_pagos":
        numeric = df.select_dtypes(include="number")
        if not numeric.empty:
            ult = numeric.iloc[-1, 0]
            valor_str, _ = _formatear(ult, "millones USD")
            col.metric(f"{meta['nombre']} — {meta['fuente']}", valor_str)

    elif name == "ipc":
        ipc_cols = [c for c in df.columns if "total" in c.lower() and c != "fecha"]
        if ipc_cols:
            serie = df[ipc_cols[0]].dropna()
            ultimo = serie.iloc[-1]
            ant = serie.iloc[-13] if len(serie) > 13 else serie.iloc[0]
            var = ((ultimo - ant) / ant) * 100 if ant else 0
            var_str = f"{'+' if var > 0 else ''}{var:.1f}% anual"
            if "fecha" in df.columns:
                fecha_str = pd.to_datetime(df["fecha"].iloc[-1]).strftime("%b %Y")
            col.metric(f"{meta['nombre']} — {meta['fuente']}", f"{ultimo:.1f}", var_str)

    spark = None
    try:
        if "serie" in dir() and len(serie) > 2:
            spark = _sparkline(serie)
    except Exception:
        spark = None
    if spark:
        col.plotly_chart(spark, use_container_width=True)

    col.caption(f"Ultimo dato: {fecha_str}")


def mostrar(datasets):
    st.markdown(
        "Panorama de los principales indicadores macroeconomicos de Panama. "
        "Datos del **INEC**, **Contraloria General** y **MEF**."
    )

    cols = st.columns(5)
    for i, name in enumerate(["imae", "pib_constante", "importaciones_valor", "deuda_publica", "ipc"]):
        _tarjeta(datasets, name, cols[i])

    st.divider()
    st.subheader("Ultimos valores por indicador")

    data_rows = []
    nombres = {
        "imae": "IMAE (Actividad Economica)",
        "pib_constante": "PIB Real Trimestral",
        "importaciones_valor": "Importaciones (Valor CIF)",
        "exportaciones": "Exportaciones",
        "balanza_pagos": "Balanza de Pagos",
        "ipc": "IPC (Inflacion)",
        "deuda_publica": "Deuda Publica",
        "ejecucion_presupuestaria": "Ej. Presupuestaria",
        "sociodemograficos": "Indicadores Sociodemograficos",
    }
    fuentes = {
        "imae": "INEC", "pib_constante": "INEC", "importaciones_valor": "INEC",
        "exportaciones": "INEC", "balanza_pagos": "INEC", "ipc": "INEC",
        "deuda_publica": "MEF", "ejecucion_presupuestaria": "Contraloria",
        "sociodemograficos": "INEC",
    }

    for name, label in nombres.items():
        df = datasets.get(name)
        if df is None or len(df) == 0:
            continue
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            continue
        first_num = numeric.columns[0]
        ultimo = numeric[first_num].dropna()
        if len(ultimo) == 0:
            continue
        val = ultimo.iloc[-1]
        fecha = "-"
        if "fecha" in df.columns:
            f = df["fecha"].dropna()
            if len(f) > 0:
                try:
                    fecha = pd.to_datetime(f.iloc[-1]).strftime("%b %Y")
                except Exception:
                    fecha = str(f.iloc[-1])
        valor_str = f"{val:,.0f}" if abs(val) > 1000 else f"{val:,.2f}"
        data_rows.append({
            "Indicador": label,
            "Fuente": fuentes.get(name, "-"),
            "Ultimo valor": valor_str,
            "Periodo": fecha,
        })

    if data_rows:
        df_table = pd.DataFrame(data_rows)
        st.dataframe(df_table, hide_index=True, use_container_width=True)

    with st.expander("Fuente de datos"):
        st.markdown("""
        Los datos provienen del portal [datosabiertos.gob.pa](https://datosabiertos.gob.pa)
        del Gobierno de Panama, que expone datasets del INEC, MEF, Contraloria y otras
        instituciones a traves de la API CKAN. La descarga y actualizacion de los datos
        se realiza mediante `python run.py` (con o sin `--force`).
        """)

    st.divider()
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.markdown("""
        **Grupo 2 — 1GS242**
        Cesar Santiago | Jean Suarez | Diego Vina | Simon Espino
        Topicos Especiales de Gestion de la Informacion — Prof. Reinel Aguirre
        [github.com/aaacmsg/topicos_parcial2](https://github.com/aaacmsg/topicos_parcial2)
        """)
