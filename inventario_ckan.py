"""
Inventario de datos económicos disponibles en CKAN (datosabiertos.gob.pa)
Busca datasets relevantes para: PIB, IMAE, IPC, desempleo, comercio, balanza de pagos,
finanzas públicas, turismo, indicadores bancarios
"""
import requests, json, csv, os
from datetime import datetime

BASE = "https://datosabiertos.gob.pa/api/3/action"
OUTPUT = os.path.join(os.path.dirname(__file__), "inventario_ckan_resultados.txt")

queries = [
    # Temas económicos clave
    "PIB producto interno bruto",
    "IMAE indice actividad economica",
    "IPC indice precios consumidor inflacion",
    "desempleo empleo mercado laboral",
    "balanza de pagos",
    "comercio exterior exportacion importacion",
    "turismo llegadas visitantes",
    "finanzas publicas presupuesto fiscal",
    "deuda publica",
    "salario ingreso",
]

results = []

def fetch_dataset(id_or_name):
    r = requests.get(f"{BASE}/package_show", params={"id": id_or_name}, timeout=20)
    return r.json() if r.ok else None

def get_recent_date(resources):
    """Try to extract a date from resource names/descriptions"""
    import re
    dates = []
    for res in resources:
        name = (res.get("name") or "") + " " + (res.get("description") or "")
        # Look for years 20xx
        years = re.findall(r"(20\d{2})", name)
        for y in years:
            dates.append(y)
    return max(dates) if dates else "N/A"

print("=" * 80)
print("INVENTARIO DE DATOS ECONÓMICOS - CKAN PANAMÁ")
print("Escaneando datasets...")
print("=" * 80)

seen = set()

for q in queries:
    print(f"\n--- Buscando: '{q}' ---")
    r = requests.get(
        f"{BASE}/package_search",
        params={"q": q, "rows": 30},
        timeout=20,
    )
    if not r.ok:
        print(f"  Error: {r.status_code}")
        continue

    data = r.json()
    if not data.get("success"):
        continue

    for ds in data["result"]["results"]:
        ds_id = ds["id"]
        if ds_id in seen:
            continue
        seen.add(ds_id)

        title = ds["title"]
        org = ds.get("organization", {}).get("title", "N/A") if ds.get("organization") else "N/A"
        notes = (ds.get("notes") or "")[:200]
        resources = ds.get("resources", [])

        # Collect formats
        formats = {}
        for res in resources:
            fmt = (res.get("format") or "N/A").upper()
            created = res.get("created", "")[:10]
            url = res.get("url", "")
            formats[fmt] = {"date": created, "url": url}

        # Determine periodicity from notes or tags
        tags = [t["name"] for t in ds.get("tags", [])]
        notes_lower = notes.lower()

        periodicidad = "No especificada"
        if any(w in notes_lower or w in tags for w in ["mensual", "mensuales"]):
            periodicidad = "Mensual"
        elif any(w in notes_lower or w in tags for w in ["trimestral", "trimestrales"]):
            periodicidad = "Trimestral"
        elif any(w in notes_lower or w in tags for w in ["anual", "anuales"]):
            periodicidad = "Anual"
        elif any(w in notes_lower or w in tags for w in ["semestral"]):
            periodicidad = "Semestral"
        elif any(w in notes_lower or w in tags for w in ["diario", "diaria", "diarias"]):
            periodicidad = "Diario"
        elif any(w in notes_lower or w in tags for w in ["semanal", "semanales"]):
            periodicidad = "Semanal"

        # Get formats
        formatos_disponibles = ", ".join(formats.keys()) if formats else "N/A"

        # Get latest resource date
        recientes = [f["date"] for f in formats.values() if f["date"]]
        fecha_reciente = max(recientes) if recientes else "N/A"

        row = {
            "titulo": title,
            "organizacion": org,
            "periodicidad": periodicidad,
            "fecha_reciente": fecha_reciente,
            "formatos": formatos_disponibles,
            "notas": notes[:100],
            "tags": ", ".join(tags[:5]),
            "id": ds_id,
        }
        results.append(row)

        print(f"\n  [{len(results)}] {title}")
        print(f"      Org: {org}")
        print(f"      Tags: {', '.join(tags[:5])}")
        print(f"      Formatos: {formatos_disponibles}")
        print(f"      Fecha reciente: {fecha_reciente}")
        print(f"      Periodo: {periodicidad}")

# Now also search specifically for INEC datasets with economic indicators
print("\n\n--- Buscando datasets específicos del INEC ---")
for term in ["PIB", "IMAE", "IPC", "empleo", "balanza", "comercio"]:
    r = requests.get(
        f"{BASE}/package_search",
        params={"q": f"INEC {term}", "rows": 20},
        timeout=20,
    )
    if not r.ok:
        continue
    data = r.json()
    if not data.get("success"):
        continue
    for ds in data["result"]["results"]:
        ds_id = ds["id"]
        if ds_id in seen:
            continue
        seen.add(ds_id)
        title = ds["title"]
        org = ds.get("organization", {}).get("title", "N/A")
        notes = (ds.get("notes") or "")[:200]
        resources = ds.get("resources", [])
        tags = [t["name"] for t in ds.get("tags", [])]

        formats = {}
        for res in resources:
            fmt = (res.get("format") or "N/A").upper()
            created = res.get("created", "")[:10]
            formats[fmt] = created

        periodicidad = "No especificada"
        nl = notes.lower()
        if any(w in nl for w in ["mensual"]): periodicidad = "Mensual"
        elif any(w in nl for w in ["trimestral"]): periodicidad = "Trimestral"
        elif any(w in nl for w in ["anual"]): periodicidad = "Anual"

        recientes = [f for f in formats.values() if f]
        fecha_reciente = max(recientes) if recientes else "N/A"
        formatos_str = ", ".join(formats.keys())

        row = {
            "titulo": title,
            "organizacion": org,
            "periodicidad": periodicidad,
            "fecha_reciente": fecha_reciente,
            "formatos": formatos_str,
            "notas": notes[:100],
            "tags": ", ".join(tags[:5]),
            "id": ds_id,
        }
        results.append(row)
        print(f"\n  [{len(results)}] {title}")
        print(f"      Org: {org}")
        print(f"      Formatos: {formatos_str}")
        print(f"      Fecha reciente: {fecha_reciente}")
        print(f"      Periodo: {periodicidad}")

# --- WRITE RESULTS FILE ---
lines = []
lines.append("=" * 80)
lines.append("INVENTARIO DE DATOS ECONÓMICOS - CKAN PANAMÁ (datosabiertos.gob.pa)")
lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
lines.append(f"Total datasets relevantes encontrados: {len(results)}")
lines.append("=" * 80)
lines.append("")

# Group by organization
orgs = {}
for row in results:
    orgs.setdefault(row["organizacion"], []).append(row)

for org, datasets in sorted(orgs.items()):
    lines.append(f"\n{'─' * 70}")
    lines.append(f"ORGANIZACIÓN: {org}  ({len(datasets)} datasets)")
    lines.append(f"{'─' * 70}")
    lines.append(f"{'#':<4} {'Dataset':<55} {'Periodo':<15} {'Actualizado':<15} {'Formatos':<20}")
    lines.append(f"{'─' * 4} {'─' * 55} {'─' * 15} {'─' * 15} {'─' * 20}")
    for i, d in enumerate(datasets, 1):
        lines.append(f"{i:<4} {d['titulo'][:54]:<55} {d['periodicidad']:<15} {d['fecha_reciente']:<15} {d['formatos'][:19]:<20}")

lines.append("\n\n")
lines.append("=" * 60)
lines.append("DATOS MÁS RELEVANTES PARA EL PROYECTO")
lines.append("=" * 60)

# Find PIB, IMAE, IPC, Empleo
keywords = {"PIB": [], "IMAE": [], "IPC/Inflacion": [], "Empleo": [], "Balanza Pagos": [], "Comercio": [], "Turismo": [], "Finanzas": [], "Salarios": []}
for row in results:
    t = row["titulo"].lower()
    n = row["notas"].lower()
    txt = t + " " + n
    if "producto interno" in txt or ("pib" in txt and "pib" not in keywords["PIB"]):
        keywords["PIB"].append(row)
    if "imae" in txt or "indice de la actividad" in txt:
        keywords["IMAE"].append(row)
    if "ipc" in txt or "indice de precios" in txt or "inflacion" in txt:
        keywords["IPC/Inflacion"].append(row)
    if "empleo" in txt or "desempleo" in txt or "mercado laboral" in txt or "ocupacion" in txt:
        keywords["Empleo"].append(row)
    if "balanza de pagos" in txt:
        keywords["Balanza Pagos"].append(row)
    if "comercio exterior" in txt or "exportacion" in txt or "importacion" in txt:
        keywords["Comercio"].append(row)
    if "turismo" in txt or "llegada" in txt:
        keywords["Turismo"].append(row)
    if "finanza" in txt or "fiscal" in txt or "presupuesto" in txt or "deuda" in txt:
        keywords["Finanzas"].append(row)
    if "salario" in txt or "ingreso" in txt:
        keywords["Salarios"].append(row)

for k, v in keywords.items():
    lines.append(f"\n--- {k} ({len(v)} datasets) ---")
    for d in v:
        lines.append(f"  - {d['titulo'][:50]}")
        lines.append(f"    Org: {d['organizacion']} | Periodo: {d['periodicidad']} | Último: {d['fecha_reciente']} | Formatos: {d['formatos']}")

lines.append("\n\n--- RECOMENDACIÓN ---")
lines.append("Indicadores mínimos sugeridos para el proyecto:")
lines.append("  1. PIB Trimestral (INEC)")
lines.append("  2. IMAE Mensual (INEC)")
lines.append("  3. IPC Mensual (INEC)")
lines.append("  4. Balanza de Pagos / Comercio Exterior")
lines.append("  5. Turismo (opcional)")
lines.append("")
lines.append("Fuentes: INEC + DatosAbiertos CKAN (≥2 fuentes cumplidas)")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n\n✅ Resultados guardados en: {OUTPUT}")
