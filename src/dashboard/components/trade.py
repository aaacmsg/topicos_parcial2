import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def _limpiar_nombre(col):
    col = col.replace("_", " ").strip()
    col = col.replace("bienes de consumo", "Bienes de consumo")
    col = col.replace("bienes intermedios", "Bienes intermedios")
    col = col.replace("bienes de capital", "Bienes de capital")
    return col.title()


def mostrar(datasets):
    st.markdown(
        "Evolucion del comercio exterior de Panama. Datos de importaciones (valor CIF y peso neto) "
        "y exportaciones por pais de destino, publicados por el **INEC**."
    )

    imp_valor = datasets.get("importaciones_valor")
    imp_peso = datasets.get("importaciones_peso")
    export = datasets.get("exportaciones")
    balanza = datasets.get("balanza_pagos")

    tab1, tab2, tab3 = st.tabs(["Importaciones (Valor)", "Importaciones (Peso)", "Exportaciones"])

    with tab1:
        if imp_valor is not None and len(imp_valor) > 0:
            tipos = [c for c in imp_valor.columns if c.startswith("bienes_") and c != "fecha"]
            if tipos:
                fig = go.Figure()
                for t in tipos:
                    fig.add_trace(go.Scatter(
                        x=imp_valor["fecha"], y=imp_valor[t],
                        mode="lines", name=_limpiar_nombre(t),
                        line=dict(width=2),
                    ))
                fig.update_layout(
                    title="Importaciones por tipo de bien — Valor CIF (USD)",
                    xaxis_title="",
                    yaxis_title="Valor (USD)",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se encontraron columnas de importaciones")
        else:
            st.warning("No hay datos de importaciones")

    with tab2:
        if imp_peso is not None and len(imp_peso) > 0:
            tipos = [c for c in imp_peso.columns if c.startswith("bienes_") and c != "fecha"]
            if tipos:
                fig = go.Figure()
                for t in tipos:
                    fig.add_trace(go.Scatter(
                        x=imp_peso["fecha"], y=imp_peso[t],
                        mode="lines", name=_limpiar_nombre(t),
                        line=dict(width=2),
                    ))
                fig.update_layout(
                    title="Importaciones por tipo de bien — Peso Neto (Kg)",
                    xaxis_title="",
                    yaxis_title="Peso (Kg)",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if export is not None and len(export) > 0:
            top_paises = export.groupby("pais_de_destino")["valor_exportacion"].sum().nlargest(10).reset_index()
            top_paises["valor_exportacion"] = top_paises["valor_exportacion"] / 1e6
            fig = px.bar(
                top_paises,
                x="valor_exportacion",
                y="pais_de_destino",
                orientation="h",
                title="Top 10 paises de destino de exportaciones (USD millones)",
                labels={"valor_exportacion": "Valor exportado (USD millones)", "pais_de_destino": ""},
                color="valor_exportacion",
                color_continuous_scale="Blues",
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Ver tabla completa"):
                tabla = export.groupby("pais_de_destino")["valor_exportacion"].sum().sort_values(ascending=False).reset_index()
                tabla.columns = ["Pais de destino", "Valor total exportado (USD)"]
                tabla["Valor total exportado (USD)"] = tabla["Valor total exportado (USD)"].apply(lambda x: f"${x:,.0f}")
                st.dataframe(tabla, hide_index=True, use_container_width=True)

    with st.expander("Fuente de datos"):
        st.markdown("""
        **Importaciones:** INEC — Valor CIF y peso neto de bienes importados, por tipo (consumo, intermedio, capital).  
        **Exportaciones:** INEC — Valor de exportaciones por pais de destino.  
        **Balanza de Pagos:** INEC — Cuenta corriente de la balanza de pagos de Panama.  
        Datos obtenidos via [datosabiertos.gob.pa](https://datosabiertos.gob.pa) (CKAN API).
        """)
