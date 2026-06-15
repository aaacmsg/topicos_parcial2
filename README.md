# Dashboard de Indicadores Economicos de Panama con IA

**Grupo 2 — 1GS242 — Topicos Especiales de Gestion de la Informacion**
**Profesor:** Reinel Aguirre — **I Semestre 2026 — UTP**

| Integrante | Cedula |
|---|---|
| Cesar Santiago | 8-1007-1423 |
| Jean Suarez | 8-1015-1661 |
| Diego Vina | 8-1019-793 |
| Simon Espino | 8-1014-1255 |

**Repositorio:** [github.com/aaacmsg/topicos_parcial2](https://github.com/aaacmsg/topicos_parcial2)

---

## Pipeline del Proyecto

![Pipeline](assets/pipeline.svg)

![Dashboard](assets/dashboard.svg)

---

## Instalacion

```bash
# 1. Clonar el repositorio
git clone https://github.com/aaacmsg/topicos_parcial2.git
cd topicos_parcial2

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt    # Windows
# .venv/bin/pip install -r requirements.txt      # Mac / Linux
```

## Ejecucion

```bash
python run.py
```

`run.py` auto-detecta el entorno virtual, descarga solo datos nuevos desde CKAN (compara fechas), preprocesa, entrena modelos y abre el dashboard en `http://localhost:8501`.

### Comandos disponibles

| Comando | Que hace |
|---------|----------|
| `python run.py` | Pipeline completo (solo descarga cambios) + dashboard |
| `python run.py --dashboard` | Solo abrir dashboard (datos ya procesados) |
| `python run.py --ingest` | Solo descargar datos (inteligente) |
| `python run.py --force` | Forzar redescarga de TODOS los datasets |
| `python run.py --ingest --force` | Forzar redescarga (sin procesar ni dashboard) |
| `python run.py --preprocess` | Solo preprocesar |
| `python run.py --train` | Solo entrenar modelos |
| `python run.py --skip-download` | Pipeline completo sin descargar |

### Pipeline inteligente

Por defecto, la descarga solo se ejecuta si CKAN tiene una version mas nueva del dataset
(compara `last_modified` del recurso contra la fecha del archivo local). Usa `--force` para
redescargar todo independientemente.

### Acceso directo a comandos de Python

```bash
.venv\Scripts\python -m src.ingest.run_ingest
.venv\Scripts\python -m src.preprocessing.run_preprocessing
.venv\Scripts\streamlit run src/dashboard/app.py
```

---

## Datasets (11)

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
| Deuda Publica | MEF | 2025 | Mensual |
| Ejecucion Presupuestaria | Contraloria | 2026 | Anual |
| Indicadores Sociodemograficos | INEC | 2013 - 2020 | Anual |

**Fuente:** [datosabiertos.gob.pa](https://datosabiertos.gob.pa) — API CKAN del Gobierno de Panama.

---

## Modelos ML

| Modelo | Indicador | Predice | Fuente |
|--------|-----------|---------|--------|
| Prophet (Meta) | IMAE | 12 meses | INEC |
| SARIMA (statsmodels) | PIB Real | 4 trimestres | INEC |

---

## Dashboard (5 vistas)

| Vista | Descripcion |
|-------|-------------|
| **Resumen** | Tarjetas con IMAE, PIB, Importaciones, Deuda, IPC + sparklines + tabla de valores |
| **Tendencias** | 8 indicadores con graficos interactivos, filtro de fechas, media movil y variacion interanual |
| **Predicciones** | Pronostico IMAE (Prophet) y PIB (ARIMA) con bandas de confianza al 80% |
| **Comercio Exterior** | Importaciones valor/peso, exportaciones top 10 paises |
| **Contexto** | Deuda publica MEF, ejecucion presupuestaria Contraloria, indicadores sociodemograficos INEC |

---

## Estructura del Proyecto

```
├── assets/               # Imagenes y diagramas
├── data/
│   ├── raw/              # CSVs descargados desde CKAN (gitignored)
│   ├── processed/        # Parquets limpios (preprocessing)
│   └── models/           # Modelos serializados (gitignored)
├── src/
│   ├── ingest/           # Cliente CKAN + config + descarga
│   ├── preprocessing/    # Pipeline de limpieza y feature engineering
│   ├── models/           # Prophet (IMAE) + ARIMA (PIB) + evaluator
│   └── dashboard/        # Streamlit app (5 componentes)
├── tests/                # Tests unitarios (26 tests)
├── run.py                # Entry point unico
├── requirements.txt
└── README.md
```

---

## Tests

```bash
python -m pytest tests/ -v
```

## Tecnologias

Python, pandas, Prophet (Meta), ARIMA (statsmodels), Streamlit, Plotly, CKAN API, Parquet.

---

**Universidad Tecnologica de Panama — Facultad de Ingenieria de Sistemas Computacionales**
**Topicos Especiales de Gestion de la Informacion — I Semestre 2026**
