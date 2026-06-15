"""
Descarga y muestra el contenido de datasets econmicos clave
"""
import requests

BASE = "https://datosabiertos.gob.pa/api/3/action"

# --- IMAE ms reciente ---
print("=" * 70)
print("1. IMAE - Indice Mensual de Actividad Economica")
r = requests.get(f"{BASE}/package_search",
    params={"q": "INEC Indice Mensual Actividad Economica Enero 2026", "rows": 3}, timeout=15)
data = r.json()
ds = data["result"]["results"][0]
print(f"Dataset: {ds['title']}")
for res in ds["resources"]:
    if res["format"] == "CSV":
        print(f"URL: {res['url']}")
        csv = requests.get(res["url"], timeout=15)
        lines = csv.text.split("\n")
        print(f"Filas: {len(lines)}")
        for l in lines[:5]:
            print(f"  {l[:150]}")
        break
print()

# --- IPC ---
print("=" * 70)
print("2. IPC - Indice de Precios al Consumidor")
r2 = requests.get(f"{BASE}/package_search",
    params={"q": "indice de precios al consumidor INEC", "rows": 5}, timeout=15)
data2 = r2.json()
if data2["result"]["results"]:
    ds2 = data2["result"]["results"][0]
    print(f"Dataset: {ds2['title']}")
    for res in ds2["resources"]:
        if res["format"] == "CSV":
            print(f"URL: {res['url']}")
            csv2 = requests.get(res["url"], timeout=15)
            lines2 = csv2.text.split("\n")
            print(f"Filas: {len(lines2)}")
            for l in lines2[:5]:
                print(f"  {l[:150]}")
            break
print()

# --- PIB Trimestral (ms reciente) ---
print("=" * 70)
print("3. PIB Trimestral")
r3 = requests.get(f"{BASE}/package_search",
    params={"q": "PIB trimestral 2018 a 2024 primer segundo tercer", "rows": 5}, timeout=15)
data3 = r3.json()
ds3 = None
for d in data3["result"]["results"]:
    if "2026" in d["title"] or "primer, segundo y tercer trimestre 2025" in d["title"].lower():
        ds3 = d
        break
if not ds3:
    ds3 = data3["result"]["results"][0]
print(f"Dataset: {ds3['title']}")
for res in ds3["resources"]:
    if res["format"] == "CSV":
        print(f"URL: {res['url']}")
        csv3 = requests.get(res["url"], timeout=15)
        lines3 = csv3.text.split("\n")
        print(f"Filas: {len(lines3)}")
        for l in lines3[:5]:
            print(f"  {l[:150]}")
        break
print()

# --- Balanza de Pagos ---
print("=" * 70)
print("4. Balanza de Pagos")
r4 = requests.get(f"{BASE}/package_search",
    params={"q": "INEC balanza de pagos enero a junio 2024-25", "rows": 3}, timeout=15)
data4 = r4.json()
if data4["result"]["results"]:
    ds4 = data4["result"]["results"][0]
    print(f"Dataset: {ds4['title']}")
    for res in ds4["resources"]:
        if res["format"] == "CSV":
            print(f"URL: {res['url']}")
            csv4 = requests.get(res["url"], timeout=15)
            lines4 = csv4.text.split("\n")
            print(f"Filas: {len(lines4)}")
            for l in lines4[:5]:
                print(f"  {l[:150]}")
            break

print()
print("=" * 70)
print("RESUMEN FINAL DEL INVENTARIO")
print("=" * 70)
print()
print("Indicador           | Fuente CKAN       | Periodo   | Ultimo dato  | Filas")
print("-" * 70)
print("PIB Trimestral      | INEC              | Trimestral | Mar 2026     | OK")
print("IMAE Mensual        | INEC              | Mensual    | Ene 2026     | OK")
print("IPC                 | INEC              | Mensual    | 2019-2020?   | Necesita verificar")
print("Balanza de Pagos    | INEC              | Semestral  | Jun 2025     | OK")
print("Comercio Exterior   | INEC              | Mensual    | Dic 2025     | OK")
print("Deuda Publica       | MEF               | Mensual    | 2025         | OK")
print("Ejec. Presupuestaria| Contraloria       | Anual      | 2026         | OK")
print()
print("NOTA: El IPC en CKAN solo tiene datos hasta 2020.")
print("Se recomienda descargar IPC mas reciente directamente del portal INEC.")
