import streamlit as st
import pandas as pd
import plotly.express as px


def mostrar(datasets):
    st.header("Tendencias Historicas")

    opciones = {
        "IMAE": ("imae", "imae_original"),
        "PIB Constante": ("pib_constante", None),
        "Importaciones Valor": ("importaciones_valor", "bienes_de_consumo"),
        "IPC Total": ("ipc", None),
    }

    seleccion = st.selectbox("Selecciona indicador", list(opciones.keys()))
    ds_name, col_name = opciones[seleccion]
    df = datasets.get(ds_name)

    if df is None or len(df) == 0:
        st.warning(f"No hay datos para {seleccion}")
        return

    if "fecha" in df.columns:
        min_fecha = df["fecha"].min()
        max_fecha = df["fecha"].max()
        rango = st.slider("Rango de fechas", min_fecha.to_pydatetime(), max_fecha.to_pydatetime(),
                          (min_fecha.to_pydatetime(), max_fecha.to_pydatetime()))
        mask = (df["fecha"] >= pd.Timestamp(rango[0])) & (df["fecha"] <= pd.Timestamp(rango[1]))
        df_filtrado = df[mask].copy()
    else:
        df_filtrado = df.copy()

    mostrar_var = st.toggle("Mostrar variacion interanual")

    if ds_name == "pib_constante":
        numeric = df_filtrado.select_dtypes(include="number")
        if not numeric.empty:
            df_plot = pd.DataFrame({"fecha": df_filtrado.iloc[:, 0], "valor": numeric.sum(axis=1)})
            if mostrar_var and len(df_plot) > 1:
                df_plot["variacion"] = df_plot["valor"].pct_change(periods=4) * 100
                fig = px.line(df_plot, x="fecha", y="variacion", title="PIB - Variacion Interanual (%)")
            else:
                fig = px.line(df_plot, x="fecha", y="valor", title="PIB Total Trimestral")
            st.plotly_chart(fig, use_container_width=True)

    elif col_name and col_name in df_filtrado.columns:
        fig = px.line(df_filtrado, x="fecha", y=col_name, title=seleccion)
        st.plotly_chart(fig, use_container_width=True)

    elif ds_name == "ipc":
        ipc_cols = [c for c in df_filtrado.columns if "total" in c.lower() and c != "fecha"]
        if ipc_cols:
            fig = px.line(df_filtrado, x="fecha", y=ipc_cols[0], title="IPC Total Mensual")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Columnas disponibles:", list(df_filtrado.columns))

    else:
        st.write("Vista previa de datos:")
        st.dataframe(df_filtrado.head(10))
