"""
Funciones compartidas para el dashboard.
Centraliza logica de limpieza y extraccion de datos.
"""
import pandas as pd

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}


def find_date_col(df):
    """Encuentra columna de fecha en un dataframe. Prioriza `fecha` exacto, luego año."""
    for c in df.columns:
        if c.lower().strip() == "fecha":
            return c
    for c in df.columns:
        lower = c.lower().strip()
        if lower.startswith("a") and lower.endswith("o") and len(lower) <= 4:
            return c
    return None


def get_deuda_fecha_saldo(df):
    """Para deuda_publica: combina columna anio (float) + mes (string) para crear fechas datetime.
    Retorna (fechas_series, saldo_series) limpias, sin filas NaN."""
    anio_col = find_date_col(df)
    if anio_col is None:
        return None, None

    mes_col = None
    for c in df.columns:
        if c.lower().strip() == "mes":
            mes_col = c
            break
    if mes_col is None:
        return None, None

    saldo_col = None
    for c in df.columns:
        if "saldo" in c.lower().replace("_", "").replace(" ", "").replace("\xa0", ""):
            saldo_col = c
            break
    if saldo_col is None:
        return None, None

    temp = df[[anio_col, mes_col, saldo_col]].copy()
    temp = temp.dropna(subset=[anio_col, saldo_col])
    if len(temp) == 0:
        return None, None

    fechas = []
    for _, row in temp.iterrows():
        try:
            anio = int(row[anio_col])
            mes = MESES.get(str(row[mes_col]).strip().lower(), 1)
            fechas.append(pd.Timestamp(year=anio, month=mes, day=1))
        except (ValueError, TypeError):
            fechas.append(pd.NaT)

    saldo = pd.to_numeric(
        temp[saldo_col].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )

    result_fechas = pd.Series(fechas, index=temp.index)
    mask = result_fechas.notna() & saldo.notna()
    return result_fechas[mask], saldo[mask]


def get_deuda_mensual(df):
    """Para deuda_publica: retorna (fechas, saldo_total_por_mes) agrupado por mes.
    Suma los saldos de todos los organismos para obtener el total mensual."""
    fechas, saldos = get_deuda_fecha_saldo(df)
    if fechas is None or len(fechas) == 0:
        return None, None
    temp = pd.DataFrame({"fecha": fechas, "saldo": saldos})
    temp["periodo"] = temp["fecha"].dt.to_period("M")
    mensual = temp.groupby("periodo")["saldo"].sum().reset_index()
    mensual = mensual.sort_values("periodo")
    mensual["fecha"] = mensual["periodo"].dt.to_timestamp()
    return mensual["fecha"], mensual["saldo"]
