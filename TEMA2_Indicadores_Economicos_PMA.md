# Tema 2: Dashboard de Indicadores Económicos de Panamá con IA

## 1. Requisitos del Segundo Parcial (Semana 9-11)

Del documento del curso:

- Identificar una problemática real con datos disponibles
- Implementar un pipeline de datos (ingesta de al menos 2 fuentes)
- Preprocesar y transformar los datos
- Aplicar al menos 1 técnica de ML (clasificación, clustering o regresión)
- Dashboard Interactivo utilizando Streamlit
- Documentación parcial del proyecto

### Evaluación

| Componente | Ponderación |
|------------|------------|
| Pipeline de datos | 30% |
| Análisis ML | 25% |
| Visualización/Dashboard | 25% |
| Documentación | 20% |

### Requisitos Técnicos

- Lenguaje: Python
- Pipeline de datos funcional y documentado
- Al menos 2 fuentes de datos diferentes
- Dashboard interactivo (Streamlit)
- Código en repositorio GitHub con README

---

## 2. Requisitos Específicos del Tema #2

- Recopilar datos del INEC y Contraloría
- Crear pipelines de actualización
- Aplicar modelos predictivos de al menos 2 indicadores
- Dashboard interactivo con tendencias
- Chatbot con RAG conectado a los datos **(ELIMINADO — indicación del profesor)**
- Comparación histórica

---

## 3. Fuentes de Datos Identificadas

### Fuente 1: INEC (Instituto Nacional de Estadística y Censo)

Vía **CKAN API** (`datosabiertos.gob.pa/api/3/action/`):

| Dataset | ID en CKAN | Periodicidad | Último Dato | Formato |
|---------|-----------|-------------|-------------|---------|
| PIB Trimestral (precios constantes) | `producto-interno-bruto-trimestral...` | Trimestral | 2026 | CSV, XLSX |
| PIB Trimestral (precios corrientes) | `pib-trimestral-corriente...` | Trimestral | 2026 | CSV, XLSX |
| IMAE (Índice Mensual Actividad Económica) | `indice-de-la-actividad-economica-imae` | **Mensual** | Ene 2026 | CSV, XLSX |
| Balanza de Pagos | `resumen-de-la-balanza-de-pagos...` | Semestral | Jun 2025 | CSV, XLSX |
| Valor Importaciones (CIF) | `valor-cif-importaciones...` | **Mensual** | Dic 2025 | CSV, XLSX |
| Peso Importaciones | `peso-neto-importaciones...` | **Mensual** | Dic 2025 | CSV, XLSX |
| Exportaciones | `valor-exportacion...` | Anual | 2019 | CSV, XLSX |
| IPC (Precios al Consumidor) | `indice-de-precios-al-consumidor...` | Mensual | 2019-2020\* | CSV |

\* IPC en CKAN limitado hasta 2020. Puede descargarse más reciente del portal INEC.

### Fuente 2: MEF (Ministerio de Economía y Finanzas)

Vía CKAN API:

| Dataset | Periodicidad | Último Dato | Formato |
|---------|-------------|-------------|---------|
| Deuda Pública 2025 | **Mensual** | May 2025 | CSV, XLSX |
| Deuda Pública 2024 | Mensual | Jul 2024 | CSV, XLSX |
| Deuda Pública 2023 | Mensual | Mar 2023 | CSV, XLSX |

### Fuente 3: Contraloría General

Vía CKAN API:

| Dataset | Periodicidad | Último Dato | Formato |
|---------|-------------|-------------|---------|
| Ejecución Presupuestaria 2026 | Anual | May 2026 | CSV, XLSX |
| Ejecución Presupuestaria 2025 | Anual | Ene 2026 | CSV, XLSX |

### Total de organizaciones publicando en CKAN Panamá: 113
### Total de datasets económicos identificados: 177

Ver `inventario_ckan_resultados.txt` para el listado completo.

---

## 4. Pipeline Propuesto

```
INGESTA (CKAN API) → PREPROCESAMIENTO → ALMACENAMIENTO → ML → DASHBOARD
```

### 4.1 Ingesta

```
src/ingest/
├── ckan_client.py      # Cliente genérico para CKAN API
├── imae.py             # Ingesta de IMAE mensual
├── pib.py              # Ingesta de PIB trimestral
├── comercio.py         # Ingesta de importaciones/exportaciones
└── deuda.py            # Ingesta de deuda pública (MEF)
```

### 4.2 Preprocesamiento

```
src/preprocessing/
└── pipeline.py         # Limpieza, unificación, encoding, normalización
```

### 4.3 Modelos ML

```
src/models/
├── prophet_model.py    # Predicción IMAE con Prophet (series temporales)
└── arima_model.py      # Predicción PIB con ARIMA/SARIMA
```

### 4.4 Dashboard

```
src/dashboard/
├── app.py              # Punto de entrada Streamlit
└── components/
    ├── overview.py     # Tarjetas con indicadores clave
    ├── trends.py       # Tendencias históricas (Plotly)
    ├── predictions.py  # Predicciones overlay
    └── filters.py      # Filtros por fecha/indicador
```

---

## 5. Tecnologías

| Propósito | Librería |
|-----------|----------|
| Ingesta API | `requests` |
| Manipulación datos | `pandas`, `numpy` |
| Almacenamiento | `pyarrow` / `fastparquet` |
| ML (series temporales) | `prophet`, `statsmodels` |
| Clustering / Clasificación | `scikit-learn` |
| Dashboard | `streamlit`, `plotly` |
| Encoding seguro | `chardet` o `charset-normalizer` |

---

## 6. Estructura del Proyecto

```
proyecto_indicadores_pma/
├── data/
│   ├── raw/               # Datos descargados originales (CSV)
│   ├── processed/         # Datos limpios (Parquet)
│   └── chroma_db/         # (opcional, si se habilita RAG)
├── src/
│   ├── ingest/            # Módulos de ingesta
│   ├── preprocessing/     # Limpieza y transformación
│   ├── models/            # Modelos predictivos
│   └── dashboard/         # Streamlit app
├── notebooks/             # EDA y experimentación
├── tests/                 # Tests unitarios
├── requirements.txt       # Dependencias
├── README.md              # Documentación del proyecto
└── .gitignore
```

---

## 7. Notas Técnicas

### CKAN API — Uso Básico

```python
import requests

BASE = "https://datosabiertos.gob.pa/api/3/action"

# Buscar datasets
r = requests.get(f"{BASE}/package_search",
    params={"q": "IMAE", "rows": 5})

# Obtener metadatos de un dataset
data = r.json()
dataset = data["result"]["results"][0]
recurso_csv = [r for r in dataset["resources"] if r["format"] == "CSV"][0]

# Descargar CSV
df = pd.read_csv(recurso_csv["url"])
```

### Consideraciones sobre Encoding

Los CSVs del INEC pueden usar `latin-1` o `ISO-8859-1`. Leer con:

```python
df = pd.read_csv(url, encoding="latin-1")
# o detectar automáticamente:
import chardet
raw = requests.get(url).content
encoding = chardet.detect(raw)["encoding"]
df = pd.read_csv(url, encoding=encoding)
```

### IMAE — Estructura Confirmada

Columnas: `Mes/Año`, `SERIE ORIGINAL`, `TENDENCIA CICLO`
Filas: 123 registros desde enero 2016 hasta enero 2026.
Formato de fecha: `16-ene`, `16-feb`, ... `26-ene` (año-mes abreviado).

---

## 8. Referencias

- Portal CKAN Panamá: https://datosabiertos.gob.pa
- API CKAN Docs: https://docs.ckan.org/en/2.9/api/
- INEC: https://www.inec.gob.pa
- MEF (Deuda Pública): https://www.mef.gob.pa
- Contraloría: https://www.contraloria.gob.pa
- Prophet: https://facebook.github.io/prophet/
- Streamlit: https://streamlit.io
