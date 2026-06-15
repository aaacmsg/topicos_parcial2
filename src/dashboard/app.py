import streamlit as st
from src.dashboard.components import overview, trends, predictions, trade, context

st.set_page_config(page_title="Indicadores Economicos Panama", layout="wide")

st.title("Dashboard de Indicadores Economicos de Panama")
st.markdown(
    "Datos del **INEC**, **Contraloria General**, **Ministerio de Economia y Finanzas** "
    "y **Superintendencia de Bancos de Panama** — publicados a traves de "
    "[datosabiertos.gob.pa](https://datosabiertos.gob.pa) (CKAN API). "
    "11 indicadores macroeconomicos con modelos predictivos de series temporales."
)

datasets = overview.cargar_datos()

paginas = {
    "Resumen": overview.mostrar,
    "Tendencias": trends.mostrar,
    "Predicciones": predictions.mostrar,
    "Comercio Exterior": trade.mostrar,
    "Contexto": context.mostrar,
    "Acerca de": None,
}

seleccion = st.sidebar.radio("Navegacion", list(paginas.keys()))
st.sidebar.divider()
st.sidebar.caption("**Fuentes de datos**")
st.sidebar.caption("INEC — Instituto Nacional de Estadistica y Censo")
st.sidebar.caption("MEF — Ministerio de Economia y Finanzas")
st.sidebar.caption("Contraloria General de la Republica")
st.sidebar.caption("Superintendencia de Bancos (SBP)")
st.sidebar.caption("")
st.sidebar.caption("**Perido:** 2003 - 2026")
st.sidebar.caption("**Actualizacion:** mensual / trimestral segun indicador")

if seleccion == "Acerca de":
    st.header("Acerca de este Dashboard")
    st.markdown("""
    **Proyecto academico** — Gestion de la Informacion, I Semestre 2026
    Universidad Tecnologica de Panama, Facultad de Ingenieria de Sistemas Computacionales.

    **Tema 2:** Dashboard de Indicadores Economicos de Panama con IA.

    **Objetivo:** Integrar datos economicos publicos de Panama, aplicar modelos predictivos
    de series temporales, y visualizar los resultados en un dashboard interactivo.

    **Datasets incluidos (11):**

    | Dataset | Organismo | Periodo | Frecuencia |
    |---------|-----------|---------|------------|
    | IMAE — Indice Mensual de Actividad Economica | INEC | 2016 - 2026 | Mensual |
    | PIB Trimestral (precios constantes) | INEC | 2018 - 2025 | Trimestral |
    | PIB Trimestral (precios corrientes) | INEC | 2018 - 2025 | Trimestral |
    | Importaciones — Valor CIF | INEC | 2003 - 2025 | Mensual |
    | Importaciones — Peso Neto | INEC | 2003 - 2025 | Mensual |
    | Exportaciones por pais | INEC | 2000 - 2019 | Anual |
    | Balanza de Pagos | INEC | 2024 - 2025 | Semestral |
    | IPC — Indice de Precios al Consumidor | INEC | 2019 | Mensual |
    | Deuda Publica | MEF | 2020 - 2025 | Mensual |
    | Ejecucion Presupuestaria | Contraloria | 2026 | Anual |
    | Indicadores Sociodemograficos | INEC | 2013 - 2020 | Anual |

    **Tecnologias:** Python, pandas, Prophet (Meta), ARIMA (statsmodels), Streamlit, Plotly.
    **Fuente de datos:** [datosabiertos.gob.pa](https://datosabiertos.gob.pa) — API CKAN del Gobierno de Panama.

    ---

    **Grupo 2 — 1GS242**
    | Integrante | Cedula |
    |---|---|
    | Cesar Santiago | 8-1007-1423 |
    | Jean Suarez | 8-1015-1661 |
    | Diego Vina | 8-1019-793 |
    | Simon Espino | 8-1014-1255 |

    **Asignatura:** Topicos Especiales de Gestion de la Informacion
    **Profesor:** Reinel Aguirre

    **Repositorio:** [github.com/aaacmsg/topicos_parcial2](https://github.com/aaacmsg/topicos_parcial2)
    """)
elif seleccion:
    paginas[seleccion](datasets)

st.sidebar.divider()
st.sidebar.caption("**Grupo 2 — 1GS242**")
st.sidebar.caption("Cesar Santiago | Jean Suarez")
st.sidebar.caption("Diego Vina | Simon Espino")
st.sidebar.caption("[GitHub](https://github.com/aaacmsg/topicos_parcial2)")
