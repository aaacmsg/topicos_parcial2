# Plan de Desarrollo por Fases

**Proyecto:** Dashboard de Indicadores Económicos de Panamá con IA
**Curso:** Gestión de la Información — I Semestre 2026

---

## Fase 0: Setup del Proyecto

> Inicializar repositorio, entorno virtual y estructura base.

| Tarea | Descripción | Archivos |
|-------|-------------|----------|
| 0.1 | Crear carpeta `proyecto_indicadores_pma/` con estructura de directorios | `src/`, `data/`, `notebooks/`, `tests/` |
| 0.2 | Inicializar repositorio Git + `.gitignore` | `.gitignore` |
| 0.3 | Crear entorno virtual y `requirements.txt` | `requirements.txt` |
| 0.4 | Copiar `test_data/` descargado a `data/raw/` | `data/raw/*.csv` |

---

## Fase 1: Módulo de Ingesta (CKAN API)

> Implementar cliente CKAN genérico y módulos para cada dataset.

### 1.1 Cliente CKAN Base

| Tarea | Descripción | Archivo |
|-------|-------------|---------|
| 1.1.1 | Cliente HTTP para search + package_show + resource download | `src/ingest/ckan_client.py` |
| 1.1.2 | Función `search_datasets(query)` → lista de datasets | ↑ |
| 1.1.3 | Función `download_csv(dataset_id)` → DataFrame | ↑ |
| 1.1.4 | Función `download_all()` → descarga configurada a `data/raw/` | ↑ |

### 1.2 Módulos por Dataset

| Tarea | Dataset | Archivo |
|-------|---------|---------|
| 1.2.1 | IMAE | `src/ingest/imae.py` |
| 1.2.2 | PIB Trimestral (constante + corriente) | `src/ingest/pib.py` |
| 1.2.3 | Importaciones (valor + peso) + Exportaciones | `src/ingest/comercio.py` |
| 1.2.4 | Balanza de Pagos | `src/ingest/balanza_pagos.py` |
| 1.2.5 | IPC | `src/ingest/ipc.py` |
| 1.2.6 | Deuda Pública (MEF) | `src/ingest/deuda.py` |
| 1.2.7 | Ejecución Presupuestaria (Contraloría) | `src/ingest/presupuesto.py` |
| 1.2.8 | Indicadores Sociodemográficos | `src/ingest/sociodemografico.py` |

### 1.3 Script Unificado

| Tarea | Descripción | Archivo |
|-------|-------------|---------|
| 1.3.1 | Script que recorre todos los módulos y descarga todo | `src/ingest/run_ingest.py` |
| 1.3.2 | Tests de ingesta | `tests/test_ingest.py` |

---

## Fase 2: Preprocesamiento

> Pipeline de limpieza, estandarización y transformación.

### 2.1 Pipeline General

| Tarea | Descripción | Archivo |
|-------|-------------|---------|
| 2.1.1 | Detector de encoding automático (chardet fallback latin-1) | `src/preprocessing/pipeline.py` |
| 2.1.2 | Normalizador de separadores (`,` y `;`) | ↑ |
| 2.1.3 | Estandarizador de nombres de columnas (snake_case) | ↑ |
| 2.1.4 | Convertidor de fechas (`16-ene`, `Enero 2019` → datetime) | ↑ |
| 2.1.5 | Script que procesa `raw/*.csv` → `processed/*.parquet` | `src/preprocessing/run_pipeline.py` |

### 2.2 Feature Engineering

| Tarea | Descripción | Archivo |
|-------|-------------|---------|
| 2.2.1 | Variación interanual y mensual (%) | `src/preprocessing/pipeline.py` |
| 2.2.2 | Media móvil 3 y 12 meses | ↑ |
| 2.2.3 | Lag features (t-1, t-2, t-4, t-12) | ↑ |

---

## Fase 3: ML + Dashboard (en paralelo)

> Modelos predictivos y dashboard interactivo, en paralelo sobre `data/processed/`.

### 3.1 Modelo 1: IMAE con Prophet

| Tarea | Descripción | Archivo |
|-------|-------------|---------|
| 3.1.1 | Cargar IMAE limpio + entrenar Prophet (ds=Mes, y=IMAE) | `src/models/prophet_model.py` |
| 3.1.2 | Forecast 12 meses con bandas de confianza | ↑ |
| 3.1.3 | Evaluar: RMSE, MAE, MAPE (train/test split 80/20) | ↑ |
| 3.1.4 | Guardar modelo (pickle) + función `predict(horizon)` | ↑ |

### 3.2 Modelo 2: PIB con ARIMA

| Tarea | Descripción | Archivo |
|-------|-------------|---------|
| 3.2.1 | Cargar PIB limpio + determinar orden ARIMA | `src/models/arima_model.py` |
| 3.2.2 | Entrenar SARIMA + forecast 4 trimestres | ↑ |
| 3.2.3 | Evaluar + guardar modelo | ↑ |

### 3.3 Dashboard (Streamlit)

| Tarea | Vista | Archivo |
|-------|-------|---------|
| 3.3.1 | App principal con navegación + carga de datos | `src/dashboard/app.py` |
| 3.3.2 | **Overview**: tarjetas con indicadores clave | `src/dashboard/components/overview.py` |
| 3.3.3 | **Tendencias**: gráfico Plotly + filtro fechas | `src/dashboard/components/trends.py` |
| 3.3.4 | **Predicciones**: histórico + forecast + bandas | `src/dashboard/components/predictions.py` |
| 3.3.5 | **Comercio Exterior**: importaciones/exportaciones | `src/dashboard/components/trade.py` |
| 3.3.6 | **Contexto**: deuda, presupuesto, sociodemográficos | `src/dashboard/components/context.py` |

### 3.4 Notebooks

| Tarea | Archivo |
|-------|---------|
| 3.4.1 | Notebook EDA de todos los datasets | `notebooks/01_eda.ipynb` |
| 3.4.2 | Notebook experimentación ML | `notebooks/02_modelos.ipynb` |

---

## Fase 4: Documentación y Entrega

| Tarea | Descripción | Archivo |
|-------|-------------|---------|
| 4.1 | README.md completo (descripción, setup, uso, capturas) | `README.md` |
| 4.2 | Verificar `requirements.txt` completo | `requirements.txt` |
| 4.3 | Commit final y push a GitHub | — |
| 4.4 | Validar `streamlit run src/dashboard/app.py` funcional | — |

---

## Timeline Sugerido

```
Semana 9:
  Fase 0 (Setup)       → 1 día
  Fase 1 (Ingesta)     → 2 días
  Fase 2 (Preproces.)  → 2 días

Semana 10:
  Fase 3 (ML + Dash)   → 5 días

Semana 11:
  Fase 3 (ML + Dash)   → 1 día
  Fase 4 (Entrega)     → 2 días
```

## Dependencias

```
F0 ──→ F1 ──→ F2 ──→ F3 (ML) ──→ F4
               └─→ F3 (Dashboard) ┘
```

Cada fase produce un artefacto que consume la siguiente. ML y Dashboard pueden ir en paralelo porque ambos consumen `data/processed/`.
