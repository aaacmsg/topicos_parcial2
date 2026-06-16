# Guion de Presentacion — Dashboard de Indicadores Economicos de Panama con IA

**Grupo 2 — 1GS242 — Topicos Especiales — Prof. Reinel Aguirre**
**I Semestre 2026 — Universidad Tecnologica de Panama**

---

## Slide 1 — Portada

**Texto en slide:**
```
Universidad Tecnologica de Panama
Facultad de Ingenieria de Sistemas Computacionales

Dashboard de Indicadores Economicos de Panama con IA

Grupo 2: Cesar Santiago, Jean Suarez, Diego Vina, Simon Espino
Topicos Especiales — I Semestre 2026 — Prof. Reinel Aguirre
```

**Guion:**
"Buenos dias profesor y companeros. Somos el Grupo 2 y les presentamos nuestro proyecto: un Dashboard de Indicadores Economicos de Panama con IA. Un sistema que integra datos economicos publicos, los procesa, aplica modelos predictivos y los visualiza en un dashboard interactivo."

---

## Slide 2 — Introduccion

**Texto en slide:**
```
Problema:
- Los datos economicos de Panama estan dispersos en multiples portales
- INEC, MEF y Contraloria publican en formatos diferentes (PDF, Excel, CSV)
- No existe un unico lugar para visualizar tendencias y predicciones

Solucion:
- Pipeline automatico que consume la API CKAN de datosabiertos.gob.pa
- Unifica 11 indicadores en un solo dashboard
- Agrega modelos predictivos (Prophet + ARIMA)
- Accesible via navegador con Streamlit
```

**Guion:**
"El problema que identificamos es que los datos economicos de Panama estan dispersos. El INEC publica en su portal, el MEF en el suyo, la Contraloria en otro. Ademas los formatos varian: PDF, Excel, CSV. No hay un solo lugar donde puedas ver el IMAE, el PIB, la deuda y las importaciones en una misma pantalla, con tendencias y predicciones.

Nuestra solucion es un pipeline automatico que descarga datos de 11 indicadores desde el portal de datos abiertos del gobierno, los unifica, aplica modelos predictivos y los presenta en un dashboard interactivo accesible desde el navegador."

---

## Slide 3 — Conceptos Clave: INEC, Contraloria y MEF

**Texto en slide:**
```
INEC — Instituto Nacional de Estadistica y Censo
- Depende de la Contraloria General
- Publica: IMAE (mensual), PIB (trimestral), IPC, importaciones,
  exportaciones, balanza de pagos, indicadores sociodemograficos
- Principal fuente de estadisticas oficiales de Panama

Contraloria General de la Republica
- Ente fiscalizador del Estado
- Publica: ejecucion presupuestaria del gobierno central

MEF — Ministerio de Economia y Finanzas
- Publica: deuda publica del sector publico
- Maneja la politica fiscal del pais
```

**Guion:**
"Vamos a explicar brevemente quienes son las instituciones detras de los datos.

El INEC es el Instituto Nacional de Estadistica y Censo, la principal fuente de estadisticas oficiales de Panama. Depende de la Contraloria General. Ellos publican el IMAE que es el Indice Mensual de Actividad Economica, el PIB trimestral, el IPC, las importaciones, exportaciones y mas.

La Contraloria General publica la ejecucion presupuestaria del gobierno.

Y el MEF, Ministerio de Economia y Finanzas, publica la deuda publica. Estas tres instituciones son nuestros proveedores de datos."

---

## Slide 4 — Conceptos Clave: Que es un Pipeline de Datos

**Texto en slide:**
```
Pipeline de Datos — Flujo automatizado de procesamiento

┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ INGESTA  │ → │ LIMPIEZA │ → │ ANALISIS │ → │ ENTREGA  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
   Obtener       Preparar       Modelar       Visualizar
   datos         los datos      y predecir    resultados

Ejemplo en nuestro proyecto:
CKAN API → CSVs → Parquets limpios → Prophet/ARIMA → Streamlit
```

**Guion:**
"Un pipeline de datos es un flujo automatizado de procesamiento. Tiene 4 etapas: primero ingestamos los datos desde la fuente, luego los limpiamos y estandarizamos, despues aplicamos analisis y modelos predictivos, y finalmente entregamos los resultados visualizados.

En nuestro proyecto el pipeline comienza en la API CKAN, pasa por archivos CSV, luego a Parquets limpios, de ahi a los modelos Prophet y ARIMA, y termina en el dashboard de Streamlit. Todo esto se ejecuta con un solo comando."

---

## Slide 5 — Fuentes de Datos: Portal CKAN

**Texto en slide:**
```
datosabiertos.gob.pa — Portal Oficial de Datos Abiertos de Panama

CKAN (Comprehensive Knowledge Archive Network):
- Plataforma open-source para publicar datos abiertos
- Usada por gobiernos de todo el mundo
- Expone una API REST para consultar y descargar datasets

Como consultamos la API:

GET /api/3/action/package_search?q=IMAE
→ Busca datasets relacionados con IMAE
→ Devuelve metadatos: titulo, organizacion, recursos, fechas

GET /api/3/action/resource_show?id={resource_id}
→ Obtiene detalles del recurso CSV
→ Incluye URL de descarga y fecha de ultima modificacion

GET {url_del_csv}
→ Descarga el archivo CSV directamente
```

**Guion:**
"Nuestros datos vienen del portal datosabiertos.gob.pa, que es el portal oficial de datos abiertos del gobierno de Panama. Este portal usa CKAN, un sistema open-source para publicar datos abiertos, creado por la Open Knowledge Foundation.

CKAN expone una API REST sencilla. Para consumirla, primero buscamos datasets con package_search usando palabras clave como 'IMAE' o 'PIB'. La API nos devuelve metadatos: el titulo del dataset, la organizacion que lo publico, los recursos disponibles y las fechas de actualizacion.

Luego, con resource_show, obtenemos el ID del recurso CSV y su fecha de ultima modificacion. Finalmente descargamos el CSV directamente desde la URL que nos proporciona la API."

---

## Slide 6 — Los 11 Indicadores

**Texto en slide:**
```
Dataset               Organismo     Periodo       Frecuencia
──────────────────────────────────────────────────────────────
IMAE                  INEC         2016-2026     Mensual
PIB Real              INEC         2018-2025     Trimestral
PIB Corriente         INEC         2018-2025     Trimestral
Importaciones (Valor) INEC         2003-2025     Mensual
Importaciones (Peso)  INEC         2003-2025     Mensual
Exportaciones         INEC         2000-2019     Anual
Balanza de Pagos      INEC         2024-2025     Semestral
IPC                   INEC         2019          Mensual
Deuda Publica         MEF          2025          Mensual
Ejec. Presupuestaria  Contraloria  2026          Anual
Sociodemograficos     INEC         2013-2020     Anual

Total: 11 datasets, 177 datasets explorados en CKAN
```

**Guion:**
"Trabajamos con 11 indicadores. El IMAE, que es nuestro indicador estrella, con datos mensuales desde 2016 hasta enero de 2026. El PIB real y corriente a nivel trimestral. Las importaciones en valor y peso desde 2003 hasta 2025. Exportaciones, balanza de pagos, IPC, deuda publica del MEF, ejecucion presupuestaria de la Contraloria e indicadores sociodemograficos del INEC.

En total exploramos 177 datasets en el portal CKAN y seleccionamos los 11 mas relevantes para el ambito macroeconomico."

---

## Slide 7 — Librerias Principales

**Texto en slide:**
```
Streamlit — Framework de dashboards en Python
- Crea aplicaciones web solo con Python (sin HTML/CSS/JS)
- Widgets interactivos: sliders, botones, selectores, graficos
- Cache inteligente con @st.cache_data
- Despliegue en segundos: streamlit run app.py

pandas — Manipulacion de datos
- Lectura de CSVs, transformacion, merge, exportacion
- Columna vertebral de las 4 etapas del pipeline

Prophet — Modelo de series temporales (Meta/Facebook)
- Predice el IMAE 12 meses hacia adelante
- Descompone en tendencia + estacionalidad anual

statsmodels — Modelo SARIMA
- Predice el PIB 4 trimestres hacia adelante
- Estadistica clasica para series temporales

Plotly — Graficos interactivos
- Zoom, hover, seleccion, exportacion PNG
- Integracion nativa con Streamlit
```

**Guion:**
"Las librerias principales son:

Streamlit, que es el corazon de nuestro dashboard. Permite crear aplicaciones web completas solo con Python, sin tocar HTML, CSS o JavaScript. Tiene widgets interactivos como sliders, botones y selectores. Y lo mejor: con un solo comando, streamlit run app.py, ya tenemos la aplicacion corriendo.

pandas es la columna vertebral de todo el procesamiento de datos.

Prophet, desarrollado por Meta, es el modelo que usamos para predecir el IMAE. Descompone automaticamente la serie en tendencia de largo plazo y estacionalidad anual.

statsmodels nos da el modelo SARIMA para el PIB.

Y Plotly genera los graficos interactivos que se ven en el dashboard, con zoom y hover para explorar los datos."

---

## Slide 8 — Modelos Predictivos: Prophet (IMAE)

**Texto en slide:**
```
Prophet — Prediccion del IMAE

Que es el IMAE?
- Indice Mensual de Actividad Economica
- Mide como va la economia de Panama mes a mes
- Se adelanta al PIB trimestral
- Publicado por el INEC

Que hace Prophet?
- Toma 121 observaciones mensuales (2016-2026)
- Identifica la tendencia: la economia panamena crece?
- Identifica la estacionalidad: hay meses mas activos?
- Proyecta los proximos 12 meses

Resultado:
- MAPE (error porcentual): ~11%
- Prediccion con banda de confianza al 80%
- Ejemplo: "El IMAE de enero 2027 sera aproximadamente 285 ± 15"
```

**Guion:**
"El primer modelo es Prophet para el IMAE.

El IMAE es el Indice Mensual de Actividad Economica, el indicador mensual mas importante de Panama. Mide como va la economia mes a mes y se adelanta al PIB trimestral. Si la economia crece, el IMAE sube; si hay una crisis, el IMAE baja.

Prophet, el modelo de Meta, toma estas 121 observaciones mensuales desde 2016 hasta 2026. Identifica automaticamente la tendencia de largo plazo —si la economia esta creciendo o no— y la estacionalidad —si hay meses tradicionalmente mas altos que otros—. Luego proyecta los proximos 12 meses.

El resultado tiene un error porcentual de aproximadamente 11%, y cada prediccion incluye una banda de confianza al 80%. Por ejemplo, podemos decir: 'El IMAE de enero de 2027 sera aproximadamente 285, con un rango probable entre 270 y 300'."

---

## Slide 9 — Modelos Predictivos: ARIMA (PIB)

**Texto en slide:**
```
SARIMA — Prediccion del PIB Real

Que es el PIB?
- Producto Interno Bruto
- Valor total de bienes y servicios producidos en Panama
- Principal indicador de crecimiento economico
- Publicado trimestralmente por el INEC

Que hace SARIMA?
- Modelo estadistico clasico
- Captura 4 componentes:
  AR: Autoregresion (depende de valores anteriores)
  I:  Diferenciacion (elimina tendencia)
  MA: Media movil (errores pasados influyen)
  S:  Estacionalidad (ciclo de 4 trimestres)
- Selecciona automaticamente el mejor orden (p,d,q)
- Proyecta los proximos 4 trimestres

Resultado:
- Predice el PIB de Panama para el proximo ano
- Ejemplo: "PIB estimado Q1 2027: $65,016 millones"
```

**Guion:**
"El segundo modelo es SARIMA para el PIB Real.

El PIB es el Producto Interno Bruto, el indicador mas importante de la economia de un pais. Mide el valor total de todos los bienes y servicios producidos. El INEC lo publica trimestralmente.

SARIMA es un modelo estadistico clasico que captura cuatro componentes: la autoregresion, que significa que el PIB de este trimestre depende del PIB de trimestres anteriores; la diferenciacion, que elimina tendencias para hacer la serie estable; la media movil, que considera errores pasados; y la estacionalidad, porque la economia tiene ciclos de 4 trimestres.

El modelo selecciona automaticamente el mejor orden de parametros probando combinaciones y eligiendo la que minimiza el AIC. Luego proyecta los proximos 4 trimestres. Por ejemplo, podemos estimar que el PIB del primer trimestre de 2027 sera de aproximadamente 65 mil millones de dolares."

---

## Slide 10 — Arquitectura del Sistema

**Texto en slide:**
```
Arquitectura Completa del Pipeline

┌─────────────────────────────────────────────────────────────────────┐
│                      PIPELINE DE DATOS                                │
├───────────────────┬──────────────────┬──────────────┬────────────────┤
│   INGESTA         │  PREPROCESAMIENTO│  MODELOS ML   │  DASHBOARD     │
├───────────────────┼──────────────────┼──────────────┼────────────────┤
│ CKAN API          │  Limpieza        │ Prophet IMAE │  Resumen       │
│ (datosabiertos    │  Encoding detect │ 12 meses     │  Tendencias    │
│  .gob.pa)         │  Estandarizar    │              │  Predicciones  │
│ requests + pandas │  Parseo fechas   │ ARIMA PIB    │  Comercio Ext. │
│ chardet           │  Feature eng     │ 4 trimestres │  Contexto      │
└────────┬──────────┴──────┬───────────┴──────┬───────┴───────┬────────┘
         │                 │                  │               │
         ▼                 ▼                  ▼               ▼
   data/raw/*.csv   data/processed/    data/models/     localhost:8501
                    *.parquet          *.pkl / *.json   Streamlit

Tecnologias:
Python 3.14 | pandas | Prophet | statsmodels | Streamlit | Plotly | Parquet
```

**Guion:**
"Esta es la arquitectura completa. Tiene 4 etapas bien definidas.

La primera es la ingesta: desde la API CKAN usando requests y pandas, con deteccion de encoding mediante chardet. Los datos se guardan como CSV en data/raw.

La segunda es el preprocesamiento: limpiamos, estandarizamos nombres de columnas, parseamos fechas en distintos formatos, y aplicamos feature engineering. El resultado son archivos Parquet en data/processed.

La tercera son los modelos: Prophet para el IMAE con prediccion a 12 meses, y SARIMA para el PIB con prediccion a 4 trimestres.

Y la cuarta es el dashboard de Streamlit con 5 vistas: Resumen, Tendencias, Predicciones, Comercio Exterior y Contexto.

Lo importante es que todo esto corre con Python puro, sin bases de datos externas ni servicios en la nube."

---

## Slide 11 — Dashboard: Las 5 Vistas

**Texto en slide:**
```
1. Resumen — Tarjetas con indicadores clave + sparklines + fuentes
   IMAE, PIB, Importaciones, Deuda, IPC

2. Tendencias — 8 indicadores con graficos interactivos
   Filtro de fechas, variacion interanual, media movil

3. Predicciones — Pronostico IMAE (Prophet) y PIB (ARIMA)
   Bandas de confianza 80%, descarga CSV, re-entrenar

4. Comercio Exterior — Importaciones valor/peso + Exportaciones
   Top 10 paises, tabs por tipo

5. Contexto — Deuda MEF, Presupuesto Contraloria, Sociodemograficos INEC
   Labels en espanol, tabs organizados
```

**Guion:**
"El dashboard tiene 5 vistas.

La vista de Resumen muestra 5 tarjetas con los indicadores principales: IMAE, PIB, Importaciones, Deuda Publica e IPC. Cada tarjeta tiene el valor actual, la variacion porcentual, la fuente del dato y un sparkline con la tendencia reciente. Debajo hay una tabla con los 11 indicadores y sus ultimos valores.

La vista de Tendencias permite explorar 8 indicadores con graficos interactivos. Podemos ajustar el rango de fechas, activar la variacion interanual o la media movil de 12 meses.

La vista de Predicciones muestra el pronostico del IMAE a 12 meses con Prophet y del PIB a 4 trimestres con ARIMA. Las bandas de confianza al 80% muestran el rango probable del valor futuro. Podemos descargar la tabla como CSV o re-entrenar los modelos con datos actualizados.

La vista de Comercio Exterior tiene las importaciones en valor y peso, y el top 10 de paises de destino de las exportaciones.

Y la vista de Contexto agrupa la deuda publica del MEF, la ejecucion presupuestaria de la Contraloria y los indicadores sociodemograficos del INEC."

---

## Slide 12 — Pipeline Inteligente

**Texto en slide:**
```
Pipeline Inteligente — No descarga lo que ya tiene

Problema: Cada vez que ejecutabamos el pipeline, descargaba
los 11 CSVs completos aunque no hubieran cambiado.

Solucion: Comparamos fechas via CKAN API

1. Cada dataset tiene un resource_id fijo en la config
2. Antes de descargar, consultamos resource_show
3. Obtenemos last_modified del recurso en CKAN
4. Comparamos con la fecha de modificacion del archivo local
5. Si el archivo local esta actualizado → SALTAMOS
6. Si CKAN tiene una version mas nueva → DESCARGAMOS

python run.py         → Solo descarga cambios (recomendado)
python run.py --force → Fuerza redescarga completa
```

**Guion:**
"Una caracteristica importante de nuestro pipeline es que es inteligente.

Inicialmente, cada vez que ejecutabamos el pipeline, descargaba los 11 CSVs completos sin importar si habian cambiado o no. Esto era ineficiente.

Entonces implementamos un sistema de comparacion de fechas. Cada dataset tiene un resource_id fijo. Antes de descargar, consultamos la API de CKAN para obtener la fecha de ultima modificacion del recurso. Comparamos esa fecha con la fecha del archivo local. Si el archivo local esta actualizado, lo saltamos. Si CKAN tiene una version mas nueva, lo descargamos.

Por defecto, python run.py solo descarga lo que cambio. Y si queremos forzar una redescarga completa, usamos python run.py --force."

---

## Slide 13 — Formato Parquet (Data Warehouse)

**Texto en slide:**
```
Por que usamos Parquet en vez de solo CSV?

CSV (data/raw/)             Parquet (data/processed/)
─────────────────           ────────────────────────
Texto plano                 Binario columnar
Sin tipos de datos          Tipado: int, float, date
Sin compresion              Comprimido (~70% menor)
Carga completa              Solo columnas necesarias
Lento en archivos grandes   10-50x mas rapido

Analogia:
CSV     = Una hoja de calculo impresa en papel
Parquet = La misma hoja en Excel con formulas y formato

El pipeline transforma:
CSVs sucios de CKAN → Parquets limpios para ML y dashboard
```

**Guion:**
"Hablemos del formato de almacenamiento. Inicialmente los datos llegan como CSV desde CKAN. Pero para el analisis y los modelos, los convertimos a Parquet.

CSV es texto plano, sin tipos de datos. Todo es string. No tiene compresion. Y para leerlo hay que cargar el archivo completo, aunque solo necesitemos una columna.

Parquet es un formato binario columnar. Los datos tienen tipos: enteros, decimales, fechas. Esta comprimido, por lo que ocupa aproximadamente 70% menos espacio. Y solo lee las columnas que necesitamos, lo que lo hace de 10 a 50 veces mas rapido.

La analogia es: CSV es como una hoja de calculo impresa en papel. Parquet es la misma hoja en Excel, con formulas, tipos de datos y formato. El pipeline transforma los CSVs sucios de CKAN en Parquets limpios listos para los modelos y el dashboard."

---

## Slide 14 — Como Ejecutar

**Texto en slide:**
```
Requisitos: Python 3.10+, conexion a internet

Instalacion:
git clone https://github.com/aaacmsg/topicos_parcial2.git
cd topicos_parcial2
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

Ejecucion:
python run.py   ← Un solo comando hace todo

Comandos:
python run.py                  # Pipeline completo + dashboard
python run.py --dashboard      # Solo abrir dashboard
python run.py --force          # Redescargar todo
python run.py --ingest         # Solo descargar

El dashboard se abre en: http://localhost:8501
```

**Guion:**
"Para ejecutar el proyecto solo necesitan Python 3.10 o superior y conexion a internet.

Clonan el repositorio, crean un entorno virtual, instalan las dependencias con pip, y ejecutan python run.py. Ese solo comando hace todo: descarga los datos, los preprocesa, entrena los modelos y abre el dashboard en http://localhost:8501.

El script run.py auto-detecta el entorno virtual, asi que no necesitan activarlo manualmente. Y por defecto solo descarga datos nuevos, ahorrando tiempo en ejecuciones repetidas."

---

## Slide 15 — Conclusiones

**Texto en slide:**
```
Logros:
- Pipeline funcional que consume la API CKAN del gobierno de Panama
- 11 indicadores macroeconomicos unificados
- 2 modelos predictivos (Prophet + ARIMA)
- Dashboard interactivo con 5 vistas
- 26 tests unitarios pasando
- Pipeline inteligente con deteccion de cambios

Tecnologias:
Python, pandas, Prophet, ARIMA, Streamlit, Plotly, Parquet

Datos: datosabiertos.gob.pa (INEC, MEF, Contraloria)

Repositorio: github.com/aaacmsg/topicos_parcial2
```

**Guion:**
"En conclusion, logramos construir un pipeline funcional que consume datos reales del gobierno de Panama, unifica 11 indicadores macroeconomicos, aplica dos modelos predictivos y los presenta en un dashboard interactivo con 5 vistas.

Todo funciona con 26 tests unitarios pasando, un pipeline inteligente que solo descarga cambios, y se ejecuta con un solo comando.

El codigo esta disponible en GitHub para quien quiera revisarlo o ejecutarlo.

Muchas gracias por su atencion. Estamos listos para preguntas."
