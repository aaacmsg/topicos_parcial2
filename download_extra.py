"""
Descarga: exportaciones, indicadores sociodemográficos, IMAE serie completa
"""
import requests, os, json

BASE = "https://datosabiertos.gob.pa/api/3/action"
OUT = r"C:\Users\aaacm\topicos\parcial2\test_data"

queries = [
    {
        "name": "exportaciones",
        "q": "INEC Valor Balboas exportacion desde Panama pais destino",
        "desc": "Exportaciones (Valor en Balboas) 2000-2019"
    },
    {
        "name": "indicadores_sociodemograficos",
        "q": "INEC Indicadores Sociodemograficos",
        "desc": "Indicadores Sociodemográficos INEC"
    },
    {
        "name": "imae_serie_completa",
        "q": "Indice de la Actividad Economica IMAE INEC serie",
        "desc": "IMAE - Índice de la Actividad Económica (dataset general)"
    },
]

results = {}
seen_ids = set()

# First, list what we already have in test_data
existing = os.listdir(OUT)
print("Ya tenemos:", existing)

for qinfo in queries:
    name = qinfo["name"]
    q = qinfo["q"]
    desc = qinfo["desc"]
    
    print(f"\n--- {desc} ---")
    print(f"Buscando: '{q}'")
    
    r = requests.get(f"{BASE}/package_search", params={"q": q, "rows": 10}, timeout=20)
    if not r.ok:
        print(f"ERROR: HTTP {r.status_code}")
        continue
    
    data = r.json()
    if not data.get("success") or not data["result"]["results"]:
        print("No results found")
        continue
    
    count = data["result"]["count"]
    print(f"Total resultados: {count}")
    
    chosen = None
    for ds in data["result"]["results"]:
        has_csv = any(res["format"] == "CSV" for res in ds.get("resources", []))
        if has_csv and ds["id"] not in seen_ids:
            chosen = ds
            break
    
    if not chosen:
        chosen = data["result"]["results"][0]
    
    seen_ids.add(chosen["id"])
    title = chosen["title"]
    notes = (chosen.get("notes") or "")[:200]
    tags = [t["name"] for t in chosen.get("tags", [])]
    print(f"Dataset: {title[:90]}")
    print(f"Tags: {tags[:5]}")
    
    resources = chosen.get("resources", [])
    csvs = [r for r in resources if r["format"] == "CSV"]
    
    if not csvs:
        print("No tiene CSV, probando XLSX...")
        csvs = [r for r in resources if r["format"] in ("XLSX", "XLS")]
    
    if not csvs:
        print("No hay recursos descargables")
        continue
    
    # Try to find the best resource
    best = csvs[0]
    # Prefer a CSV that has "serie" or "completa" or is most recent
    for r in csvs:
        rname = (r.get("name") or "").lower()
        if "serie" in rname or "completa" in rname or "general" in rname:
            best = r
            break
    
    url = best["url"]
    fmt = best["format"]
    ext = ".csv" if fmt == "CSV" else (".xlsx" if fmt == "XLSX" else ".xls")
    filepath = os.path.join(OUT, f"{name}{ext}")
    
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"Error download: HTTP {resp.status_code}")
            continue
        
        raw = resp.content
        
        import chardet
        enc = chardet.detect(raw)["encoding"] or "utf-8"
        text = raw.decode(enc, errors="replace")
        
        with open(filepath, "wb") as f:
            f.write(raw)
        
        lines = text.split("\n")
        print(f"Guardado: {filepath}")
        print(f"Encoding: {enc} | Filas: {len(lines)} | Tamaño: {len(raw)} bytes")
        print(f"Primeras 2 filas:")
        for l in lines[:3]:
            print(f"  {l.strip()[:130]}")
        
        results[name] = {"file": filepath, "rows": len(lines), "size": len(raw)}
        
    except Exception as e:
        print(f"ERROR: {e}")

# Also check if our current imae.csv already has the full series
print("\n--- Verificando IMAE existente ---")
try:
    import pandas as pd
    imae_path = os.path.join(OUT, "imae.csv")
    if os.path.exists(imae_path):
        df = pd.read_csv(imae_path, encoding="latin-1")
        print(f"imae.csv actual: {df.shape[0]} filas, {df.shape[1]} columnas")
        print(f"Columnas: {list(df.columns)}")
        print(f"Primer Mes/Año: {df.iloc[0,0]}")
        print(f"Último Mes/Año: {df.iloc[-1,0]}")
        
        # Check date range
        years = set()
        for val in df.iloc[:, 0]:
            if isinstance(val, str) and "-" in val:
                yr = val.split("-")[1]
                years.add(yr)
        print(f"Años cubiertos: {sorted(years)}")
except Exception as e:
    print(f"Error: {e}")

print("\n\nRESUMEN FINAL:")
for name, info in results.items():
    print(f"  {name}: {info['rows']} filas, {info['size']/1024:.1f} KB")
