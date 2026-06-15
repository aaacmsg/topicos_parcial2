import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.dashboard.data_utils import find_date_col, get_deuda_fecha_saldo, get_deuda_mensual

INDICADORES = {
    "IMAE (Actividad Economica)": ("imae", "imae_original", "INEC", "indice"),
    "PIB Real Trimestral": ("pib_constante", None, "INEC", "millones USD"),
    "PIB Corriente Trimestral": ("pib_corriente", None, "INEC", "millones USD"),
    "Importaciones (Valor CIF)": ("importaciones_valor", "bienes_de_consumo", "INEC", "USD"),
    "Importaciones (Peso Neto)": ("importaciones_peso", "bienes_de_consumo", "INEC", "kg"),
    "IPC (Inflacion)": ("ipc", None, "INEC", "indice"),
    "Deuda Publica": ("deuda_publica", "saldo", "MEF", "millones USD"),
    "Balanza de Pagos": ("balanza_pagos", None, "INEC", "millones USD"),
}


def _cargar_serie(df, ds_name, col_name, unidad):
    if df is None or len(df) == 0:
        return None, None

    if ds_name == "pib_constante" or ds_name == "pib_corriente":
        numeric = df.select_dtypes(include="number")
        if numeric.shape[1] < 2:
            return None, None
        serie = numeric.sum(axis=1)
        fechas = df.iloc[:, 0].astype(str)
        return fechas, serie

    if ds_name == "ipc":
        ipc_cols = [c for c in df.columns if "total" in c.lower() and c != "fecha"]
        if not ipc_cols:
            return None, None
        fcol = find_date_col(df)
        if fcol:
            return df[fcol], df[ipc_cols[0]]
        return None, None

    if ds_name == "deuda_publica":
        fechas, saldo = get_deuda_mensual(df)
        if fechas is not None and saldo is not None:
            return fechas, saldo
        return None, None

    if ds_name == "balanza_pagos":
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            return None, None
        return pd.Series(df.index.values), numeric.iloc[:, 0]

    if col_name and col_name in df.columns:
        fcol = find_date_col(df)
        if fcol:
            return df[fcol], df[col_name]
        return None, None

    return None, None


def _formatear_eje_y(unidad, valor):
    if unidad == "millones USD":
        return f"${valor:,.0f}M"
    if unidad == "USD":
        if abs(valor) >= 1e9:
            return f"${valor/1e9:.1f}MM"
        return f"${valor:,.0f}"
    return f"{valor:,.0f}"


def mostrar(datasets):
    st.markdown(
        "Evolucion historica de los indicadores economicos. "
        "Selecciona el indicador y ajusta el rango de fechas para explorar tendencias."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        seleccion = st.selectbox("Indicador", list(INDICADORES.keys()))
    with col2:
        pass

    ds_name, col_name, fuente, unidad = INDICADORES[seleccion]
    df = datasets.get(ds_name)
    if df is None or len(df) == 0:
        st.warning(f"No hay datos disponibles para {seleccion}")
        return

    fechas, serie = _cargar_serie(df, ds_name, col_name, unidad)
    if fechas is None or serie is None:
        st.warning(f"No se pudo cargar la serie para {seleccion}")
        return

    primer_valor = fechas.iloc[0] if hasattr(fechas, "iloc") else fechas[0]
    if "fecha" not in str(type(fechas)).lower() and "datetime" not in str(type(primer_valor)).lower():
        try:
            fechas = pd.to_datetime(fechas)
        except Exception:
            pass

    col_f, col_t = st.columns([3, 1])
    with col_f:
        min_d = fechas.min() if hasattr(fechas, "min") else fechas.iloc[0]
        max_d = fechas.max() if hasattr(fechas, "max") else fechas.iloc[-1]
        try:
            rango = st.slider(
                "Rango de fechas",
                min_value=min_d.to_pydatetime() if hasattr(min_d, "to_pydatetime") else min_d,
                max_value=max_d.to_pydatetime() if hasattr(max_d, "to_pydatetime") else max_d,
                value=(
                    min_d.to_pydatetime() if hasattr(min_d, "to_pydatetime") else min_d,
                    max_d.to_pydatetime() if hasattr(max_d, "to_pydatetime") else max_d,
                ),
                format="MMM YYYY",
            )
            mask = (fechas >= pd.Timestamp(rango[0])) & (fechas <= pd.Timestamp(rango[1]))
            fechas_f = fechas[mask]
            serie_f = serie[mask]
        except Exception:
            fechas_f = fechas
            serie_f = serie

    with col_t:
        mostrar_var = st.toggle("Variacion interanual", value=False)
        mostrar_media = st.toggle("Media movil 12m", value=False)

    if mostrar_var:
        serie_plot = serie_f.pct_change(periods=12) * 100
        titulo_eje_y = "Variacion interanual (%)"
    else:
        serie_plot = serie_f
        titulo_eje_y = seleccion

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fechas_f, y=serie_plot, mode="lines",
        name=seleccion, line=dict(width=2, color="#1f77b4"),
    ))

    if mostrar_media and not mostrar_var:
        mm = serie_f.rolling(window=12, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=fechas_f, y=mm, mode="lines",
            name="Media movil 12m", line=dict(width=1.5, color="orange", dash="dash"),
        ))

    fig.update_layout(
        title=f"{seleccion} — Fuente: {fuente}",
        xaxis_title="",
        yaxis_title=titulo_eje_y,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b, col_c, col_d = st.columns(4)
    validos = serie_f.dropna()
    if len(validos) > 0:
        ult = validos.iloc[-1]
        prom = validos.mean()
        mini = validos.min()
        maxi = validos.max()
        if mostrar_var:
            col_a.metric("Ultimo", f"{ult:.2f}%")
            col_b.metric("Promedio", f"{prom:.2f}%")
            col_c.metric("Minimo", f"{mini:.2f}%")
            col_d.metric("Maximo", f"{maxi:.2f}%")
        else:
            col_a.metric("Ultimo", _formatear_eje_y(unidad, ult))
            col_b.metric("Promedio", _formatear_eje_y(unidad, prom))
            col_c.metric("Minimo", _formatear_eje_y(unidad, mini))
            col_d.metric("Maximo", _formatear_eje_y(unidad, maxi))

    with st.expander("Fuente de datos"):
        st.markdown(f"""
        **{seleccion}**  
        Publicado por: **{fuente}**  
        Frecuencia: {"mensual" if "Mensual" in seleccion or "IMAE" in seleccion or "IPC" in seleccion or "Importaciones" in seleccion else "trimestral" if "Trimestral" in seleccion else "semestral" if "Balanza" in seleccion else "anual"}  
        Unidad: {unidad}  
        Datos obtenidos via [datosabiertos.gob.pa](https://datosabiertos.gob.pa) (CKAN API)
        """)
