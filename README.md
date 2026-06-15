# Dashboard de Indicadores Economicos de Panama con IA

Dashboard interactivo que integra datos economicos publicos de Panama (INEC, MEF, Contraloria) via CKAN API, aplica modelos predictivos de series temporales, y visualiza resultados en Streamlit.

## Estructura del Proyecto

```
parcial2/
├── data/
│   ├── raw/              # CSVs descargados desde CKAN (gitignored)
│   ├── processed/        # Parquets limpios generados por preprocessing
│   └── models/           # Modelos serializados (gitignored)
├── src/
│   ├── ingest/           # Cliente CKAN + config + script de descarga
│   ├── preprocessing/    # Pipeline de limpieza y transformacion
│   ├── models/           # Prophet (IMAE) + ARIMA (PIB)
│   └── dashboard/        # Streamlit app con 5 vistas
├── tests/                # Tests unitarios
├── notebooks/            # EDA y experimentacion
├── requirements.txt
├── PRD.md
├── PLAN_DESARROLLO.md
└── README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Uso

### 1. Descargar datos desde CKAN

```bash
.venv\Scripts\python -m src.ingest.run_ingest
```

Descarga 11 datasets economicos de datosabiertos.gob.pa a `data/raw/`.

### 2. Preprocesar datos

```bash
.venv\Scripts\python -m src.preprocessing.run_preprocessing
```

Limpia, estandariza y genera Parquets en `data/processed/`.

### 3. Entrenar modelos

```bash
.venv\Scripts\python -c "from src.models.prophet_model import entrenar_completo; entrenar_completo()"
.venv\Scripts\python -c "from src.models.arima_model import entrenar_completo; entrenar_completo()"
```

### 4. Ejecutar dashboard

```bash
.venv\Scripts\streamlit run src/dashboard/app.py
```

## Datasets (11)

| Dataset | Fuente | Periodo | Ultimo dato |
|---------|--------|---------|-------------|
| IMAE | INEC | Mensual | Ene 2026 |
| PIB Trimestral | INEC | Trimestral | 2025 |
| Importaciones (valor + peso) | INEC | Mensual | Dic 2025 |
| Exportaciones | INEC | Anual | 2019 |
| Balanza de Pagos | INEC | Semestral | Jun 2025 |
| IPC | INEC | Mensual | 2019 |
| Deuda Publica | MEF | Mensual | 2025 |
| Ejecucion Presupuestaria | Contraloria | Anual | 2026 |
| Indicadores Sociodemograficos | INEC | Anual | 2020 |

**Fuente unificada:** https://datosabiertos.gob.pa (CKAN API)

## Modelos ML

| Modelo | Indicador | Tecnica | Horizonte |
|--------|-----------|---------|-----------|
| Prophet | IMAE | Series temporales bayesianas | 12 meses |
| ARIMA | PIB | SARIMA estacional | 4 trimestres |

## Dashboard

5 vistas en Streamlit:
- **Resumen** - Tarjetas con indicadores clave
- **Tendencias** - Graficos interactivos con filtros
- **Predicciones** - Forecast con bandas de confianza + descarga CSV
- **Comercio Exterior** - Importaciones y exportaciones
- **Contexto** - Deuda, presupuesto y sociodemograficos

## Tests

```bash
.venv\Scripts\python -m pytest tests/ -v
```

## Tecnologias

Python, pandas, Prophet, ARIMA (statsmodels), Streamlit, Plotly, CKAN API, Parquet.

## Licencia

Proyecto academico - Gestion de la Informacion, I Semestre 2026.
