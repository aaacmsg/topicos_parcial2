"""
Configuracion de preprocesamiento por dataset.
Todos los CSVs estan en data/raw/ guardados con utf-8-sig y separados por coma.
"""

PREP_CONFIG = {
    "imae": {
        "rename_cols": {"Mes/A\u00f1o": "fecha", "SERIE ORIGINAL": "imae_original", "TENDENCIA CICLO": "imae_tendencia"},
        "drop_cols": ["Unnamed: 3", "Unnamed: 4", "Unnamed: 5"],
        "date_parser": "imae",
        "feature_eng": ["variacion_interanual", "media_movil_12"],
    },
    "pib_constante": {
        "reparse_semicolon": True,
        "unpivot": {"id_vars": ["actividad"], "var_name": "ano", "value_name": "pib_constante"},
        "feature_eng": ["variacion_interanual"],
    },
    "pib_corriente": {
        "reparse_semicolon": True,
        "unpivot": {"id_vars": ["actividad"], "var_name": "ano", "value_name": "pib_corriente"},
        "feature_eng": ["variacion_interanual"],
    },
    "importaciones_valor": {
        "date_parser": "anio_mes",
        "feature_eng": ["variacion_interanual"],
    },
    "importaciones_peso": {
        "rename_cols": {"A\u00d1O": "A\u00f1o", "MES": "Mes"},
        "date_parser": "anio_mes",
        "feature_eng": ["variacion_interanual"],
    },
    "exportaciones": {
        "unpivot": {"id_vars": ["pais_de_destino"], "var_name": "ano", "value_name": "valor_exportacion"},
        "feature_eng": [],
    },
    "balanza_pagos": {
        "feature_eng": [],
    },
    "ipc": {
        "reparse_semicolon": True,
        "date_parser": "anio_mes",
        "feature_eng": ["variacion_interanual", "variacion_mensual"],
    },
    "deuda_publica": {
        "date_parser": "anio_mes",
        "feature_eng": [],
    },
    "ejecucion_presupuestaria": {
        "skip_rows": 5,
        "feature_eng": [],
    },
    "sociodemograficos": {
        "reparse_semicolon": True,
        "feature_eng": [],
    },
}
