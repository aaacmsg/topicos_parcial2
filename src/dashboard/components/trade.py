import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def mostrar(datasets):
    st.header("Comercio Exterior")

    imp_valor = datasets.get("importaciones_valor")
    imp_peso = datasets.get("importaciones_peso")
    export = datasets.get("exportaciones")

    if imp_valor is not None and len(imp_valor) > 0:
        st.subheader("Importaciones - Valor (CIF)")
        tipos = [c for c in imp_valor.columns if c.startswith("bienes_") and c != "fecha"]
        if tipos:
            fig = go.Figure()
            for t in tipos:
                fig.add_trace(go.Scatter(x=imp_valor["fecha"], y=imp_valor[t], mode="lines", name=t))
            fig.update_layout(title="Importaciones por tipo de bien (USD)")
            st.plotly_chart(fig, use_container_width=True)

    if imp_peso is not None and len(imp_peso) > 0:
        st.subheader("Importaciones - Peso Neto")
        tipos = [c for c in imp_peso.columns if c.startswith("bienes_") and c != "fecha"]
        if tipos:
            fig = go.Figure()
            for t in tipos:
                fig.add_trace(go.Scatter(x=imp_peso["fecha"], y=imp_peso[t], mode="lines", name=t))
            fig.update_layout(title="Importaciones por tipo de bien (peso)", xaxis_title="", yaxis_title="Kg")
            st.plotly_chart(fig, use_container_width=True)

    if export is not None and len(export) > 0:
        st.subheader("Exportaciones por Pais de Destino")
        top_paises = export.groupby("pais_de_destino")["valor_exportacion"].sum().nlargest(10).reset_index()
        fig = px.bar(top_paises, x="pais_de_destino", y="valor_exportacion",
                     title="Top 10 paises de destino")
        st.plotly_chart(fig, use_container_width=True)
