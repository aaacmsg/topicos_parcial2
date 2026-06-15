# PRD: Dashboard de Indicadores Económicos de Panamá con IA

**Product Requirements Document**
Curso: Gestión de la Información — I Semestre 2026
Tema: #2 — Grupo: [Por asignar]
Versión: 1.0

---

## 1. Resumen Ejecutivo

Sistema de gestión de información que integra datos económicos públicos de Panamá (INEC, MEF, Contraloría) a través de la API CKAN de Datos Abiertos, implementa modelos predictivos de series temporales para al menos 2 indicadores clave, y presenta los resultados en un dashboard interactivo construido con Streamlit.

---

## 2. Objetivos

### General
Desarrollar un pipeline de datos que ingiera, procese, analice y visualice indicadores económicos de Panamá para apoyar la toma de decisiones mediante un dashboard interactivo con capacidades predictivas.

### Específicos
1. Ingresar datos desde el portal Datos Abiertos de Panamá (CKAN API) — mínimo 2 fuentes institucionales (INEC + MEF/Contraloría).
2. Preprocesar y unificar series de diferentes formatos y codificaciones.
3. Implementar modelos predictivos de series temporales para IMAE (Prophet) y PIB (ARIMA).
4. Construir dashboard interactivo en Streamlit con tendencias, predicciones y comparaciones históricas.
5. Documentar todo el pipeline técnico y de uso.

---

## 3. Fuentes de Datos

### Portal Único: Datos Abiertos de Panamá (CKAN)
**URL:** https://datosabiertos.gob.pa
**API:** https://datosabiertos.gob.pa/api/3/action/
**Costo:** Gratuito — sin API key requerida
**Organizaciones publicando:** 113
**Total datasets económicos identificados:** 177

### Datasets Seleccionados

| # | Dataset | Organización | Periodo | Último Dato | Filas | Uso |
|---|---------|-------------|---------|-------------|-------|-----|
| 1 | IMAE (Índice Mensual Actividad Económica) | INEC | Mensual | Ene 2026 | 123 | **Modelo predictivo #1** |
| 2 | PIB Trimestral (precios constantes) | INEC | Trimestral | Mar 2026 | 33 | **Modelo predictivo #2** |
| 3 | PIB Trimestral (precios corrientes) | INEC | Trimestral | Mar 2026 | 64 | Comparación nominal vs real |
| 4 | Valor Importaciones (CIF) | INEC | Mensual | Dic 2025 | 276 | Análisis comercio exterior |
| 5 | Peso Importaciones | INEC | Mensual | Dic 2025 | 276 | Análisis comercio exterior |
| 6 | Exportaciones x País | INEC | Anual | 2019 | 161 | Balanza comercial |
| 7 | Balanza de Pagos | INEC | Semestral | Jun 2025 | 151 | Sector externo |
| 8 | IPC (Precios al Consumidor) | INEC | Mensual | 2019 | 14 | Inflación |
| 9 | Deuda Pública | MEF | Mensual | May 2025 | 495 | Finanzas públicas |
| 10 | Ejecución Presupuestaria | Contraloría | Anual | 2026 | 169 | Gasto gobierno |
| 11 | Indicadores Sociodemográficos | INEC | Anual | 2020 | 8 | Contexto poblacional |

### Mecanismo de Ingesta
Todos los datos se obtienen mediante la **API REST CKAN** estándar:
```
GET /api/3/action/package_search?q={query}
GET /api/3/action/package_show?id={dataset_id}
→ Descarga directa de recursos CSV desde las URLs obtenidas
```

---

## 4. Arquitectura del Pipeline

```
┌────────────┐    ┌──────────────┐    ┌────────────┐    ┌──────────────┐    ┌─────────────┐
│  INGESTA   │ →  │ PREPROCESAR  │ →  │ ALMACENAR  │ →  │  ANALIZAR    │ →  │ VISUALIZAR  │
│            │    │              │    │            │    │              │    │             │
│ CKAN API   │    │ Encoding     │    │ Parquet    │    │ Prophet      │    │ Streamlit   │
│ requests  │    │ Separadores  │    │ (columnares)│   │ ARIMA        │    │ Plotly      │
│ pandas     │    │ Normalizar   │    │            │    │ sklearn      │    │ Filters     │
│            │    │ Feature eng. │    │            │    │              │    │             │
└────────────┘    └──────────────┘    └────────────┘    └──────────────┘    └─────────────┘
```

### 4.1 Capa de Ingesta
- **Cliente CKAN genérico** (`src/ingest/ckan_client.py`): busca datasets, lista recursos, descarga CSVs.
- **Módulos específicos** por dataset: cada uno conoce la query exacta y el recurso a descargar.
- **Salida:** CSVs crudos en `data/raw/`.

### 4.2 Capa de Preprocesamiento
- Detección automática de encoding (`chardet`).
- Manejo de separadores mixtos (`,` y `;` según el dataset).
- Estandarización de nombres de columnas y formatos de fecha.
- Feature engineering (rezagos, variaciones interanuales, media móvil).
- **Salida:** Datos limpios en Parquet en `data/processed/`.

### 4.3 Capa de Modelos ML
- **Modelo 1 — IMAE con Prophet:** Predicción mensual del Índice de Actividad Económica.
  - Datos: Serie mensual 2016-2026.
  - Horizonte: 12 meses.
  - Componentes: tendencia, estacionalidad anual.
- **Modelo 2 — PIB con ARIMA/SARIMA:** Predicción trimestral del PIB real.
  - Datos: Serie trimestral 2018-2026.
  - Horizonte: 4 trimestres.
  - Evaluación: error RMSE, MAE.

### 4.4 Capa de Dashboard (Streamlit)
- **Vista General:** Tarjetas con valor actual y variación de cada indicador.
- **Tendencias Históricas:** Gráficos interactivos (Plotly) con filtro por rango de fechas.
- **Predicciones:** Serie histórica + forecast con bandas de confianza.
- **Comparación:** Período vs período (interanual, trimestral).
- **Comercio Exterior:** Evolución de importaciones/exportaciones.
- **Contexto:** Indicadores sociodemográficos y deuda pública.

---

## 5. Stack Tecnológico

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| Lenguaje | Python | 3.14+ | Plataforma principal |
| Cliente HTTP | `requests` | — | Consumir CKAN API |
| Manipulación | `pandas` / `numpy` | — | DataFrames y transformaciones |
| Almacenamiento | `pyarrow` / `fastparquet` | — | Formato columnar Parquet |
| Encoding | `chardet` | — | Detección de codificación |
| ML Series Temp. | `prophet` | — | Predicción IMAE |
| ML Series Temp. | `statsmodels` | — | Predicción PIB (ARIMA) |
| ML Adicional | `scikit-learn` | — | Clustering / métricas |
| Dashboard | `streamlit` | — | Frontend interactivo |
| Gráficos | `plotly` | — | Visualizaciones interactivas |
| Entorno | `venv` / `pip` | — | Gestión de dependencias |

---

## 6. Estructura del Proyecto

```
proyecto_indicadores_pma/
│
├── data/
│   ├── raw/                    # Datos descargados (CSV originales)
│   └── processed/              # Datos limpios (Parquet)
│
├── notebooks/
│   ├── 01_eda.ipynb            # Análisis exploratorio
│   └── 02_modelos.ipynb        # Experimentación ML
│
├── src/
│   ├── __init__.py
│   │
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── ckan_client.py      # Cliente CKAN API genérico
│   │   ├── imae.py             # Ingesta IMAE
│   │   ├── pib.py              # Ingesta PIB
│   │   ├── comercio.py         # Ingesta importaciones/exportaciones
│   │   ├── balanza_pagos.py    # Ingesta balanza de pagos
│   │   ├── deuda.py            # Ingesta deuda pública (MEF)
│   │   ├── ipc.py              # Ingesta IPC
│   │   ├── presupuesto.py      # Ingesta ejecución presupuestaria
│   │   └── sociodemografico.py # Ingesta indicadores sociodemográficos
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── pipeline.py         # Pipeline de limpieza y transformación
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── prophet_model.py    # Modelo IMAE con Prophet
│   │   ├── arima_model.py      # Modelo PIB con ARIMA
│   │   └── evaluator.py        # Métricas de evaluación
│   │
│   └── dashboard/
│       ├── __init__.py
│       ├── app.py              # Entry point Streamlit
│       └── components/
│           ├── overview.py     # Tarjetas de indicadores
│           ├── trends.py       # Gráficos de tendencias
│           ├── predictions.py  # Predicciones
│           ├── trade.py        # Comercio exterior
│           └── context.py      # Contexto adicional
│
├── tests/
│   ├── test_ingest.py
│   ├── test_preprocessing.py
│   └── test_models.py
│
├── test_data/                  # Muestras descargadas (12 datasets)
│   ├── imae.csv
│   ├── pib_trimestral_constante.csv
│   ├── pib_trimestral_corriente.csv
│   ├── ipc.csv
│   ├── balanza_pagos.csv
│   ├── importaciones_valor.csv
│   ├── importaciones_peso.csv
│   ├── exportaciones.csv
│   ├── deuda_publica.csv
│   ├── ejecucion_presupuestaria.csv
│   ├── indicadores_sociodemograficos.csv
│   └── imae_serie_completa.csv
│
├── inventario_ckan_resultados.txt  # Inventario completo CKAN (177 datasets)
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Documentación general
├── PRD.md                      # Este documento
└── .gitignore                  # Exclusiones Git
```

---

## 7. Funcionalidades del Dashboard

### 7.1 Vista General (Overview)
- 6 tarjetas con indicadores clave: IMAE, PIB, IPC, Importaciones, Deuda Pública, Desempleo proxy.
- Cada tarjeta muestra: valor actual, variación %, sparkline de tendencia.
- Refresh desde datos más recientes disponibles.

### 7.2 Tendencias Históricas
-Selector de indicador (dropdown).
- Gráfico de línea interactivo (Plotly) con zoom, hover, exportación PNG.
- Filtro por rango de fechas (slider o date picker).
- Opción de comparación interanual (toggle).

### 7.3 Predicciones
- Selector: IMAE o PIB.
- Gráfico con: datos históricos + línea de predicción + banda de confianza (80%).
- Métricas del modelo (RMSE, MAE) mostradas en sidebar.
- Botón para re-entrenar con datos actualizados.

### 7.4 Comercio Exterior
- Evolución importaciones (valor y peso) 2003-2025.
- Distribución por tipo de bien (consumo, intermedio, capital).
- Exportaciones por país de destino (años disponibles).

### 7.5 Contexto
- Deuda Pública: evolución mensual, composición por organismo.
- Ejecución Presupuestaria: ingresos vs gastos.
- Indicadores Sociodemográficos: tabla con evolución anual.

---

## 8. Criterios de Evaluación y Cumplimiento

| Criterio | % | Cómo lo cumplimos |
|----------|---|-------------------|
| Pipeline de datos | 30% | Ingesta CKAN API + preprocesamiento → Parquet |
| Análisis ML | 25% | Prophet (IMAE) + ARIMA (PIB) |
| Visualización/Dashboard | 25% | Streamlit + Plotly con 5 secciones |
| Documentación | 20% | README + PRD + código documentado + GitHub |

### Bonus tracking
| Requisito específico | Estado |
|---------------------|--------|
| Problemática real con datos disponibles | ✅ Datos públicos de Panamá |
| ≥ 2 fuentes de datos | ✅ CKAN (INEC + MEF + Contraloría) |
| Preprocesar y transformar | ✅ Pipeline de limpieza |
| ≥ 1 técnica de ML | ✅ 2 modelos (Prophet + ARIMA) |
| Dashboard Streamlit | ✅ 5 vistas interactivas |
| Documentación parcial | ✅ PRD + README |
| Código en GitHub con README | Pendiente |

---

## 9. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| CKAN API caída o lenta | Baja | Alto | Datos descargados localmente (`test_data/`) como fallback |
| Encoding inconsistente | Media | Medio | `chardet` detecta encoding automáticamente |
| IPC desactualizado en CKAN | Alta | Bajo | Usar IMAE como proxy de inflación o descargar IPC directo de INEC |
| Prophet requiere instalación C++ | Media | Medio | Usar `prophet` vía pip con precompilados |
| Formatos de fecha inconsistentes | Alta | Bajo | Pipeline de normalización de fechas |

---

## 10. Próximos Pasos

- [ ] Configurar repositorio Git e inicializar proyecto.
- [ ] Implementar módulos de ingesta para cada dataset.
- [ ] Implementar pipeline de preprocesamiento.
- [ ] Entrenar y evaluar modelos Prophet (IMAE) y ARIMA (PIB).
- [ ] Desarrollar dashboard Streamlit con todas las vistas.
- [ ] Escribir README y documentación final.
- [ ] Subir a GitHub.

---

## 11. Referencias

- Portal CKAN Panamá: https://datosabiertos.gob.pa
- API CKAN Docs: https://docs.ckan.org/en/2.9/api/
- INEC: https://www.inec.gob.pa
- MEF: https://www.mef.gob.pa
- Contraloría: https://www.contraloria.gob.pa
- Prophet: https://facebook.github.io/prophet/
- Streamlit: https://streamlit.io
- Plotly: https://plotly.com/python/
