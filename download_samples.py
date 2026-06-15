"""
Descarga de datos sample de los datasets económicos clave vía CKAN API
"""
import requests, os, json, re

BASE = "https://datosabiertos.gob.pa/api/3/action"
OUT = r"C:\Users\aaacm\topicos\parcial2\test_data"

queries = [
    {"name": "imae", "q": "INEC Indice Mensual Actividad Economica Enero 2026"},
    {"name": "pib_trimestral_constante", "q": "PIB trimestral 2018 a 2024 primer segundo tercer 2025 constante"},
    {"name": "pib_trimestral_corriente", "q": "PIB trimestral corriente 2018 a 2024 primer segundo tercer 2025"},
    {"name": "ipc", "q": "indice de precios al consumidor segun grupos"},
    {"name": "balanza_pagos", "q": "INEC balanza de pagos enero a junio 2024-25"},
    {"name": "importaciones_valor", "q": "Valor CIF importaciones acumulado Octubre 2003-2025"},
    {"name": "importaciones_peso", "q": "Peso neto importaciones acumulado Octubre 2003-2025"},
    {"name": "deuda_publica", "q": "MEF Deudas Publicas 2025"},
    {"name": "ejecucion_presupuestaria", "q": "CGR Ejecucion Presupuestaria 2026"},
]

def find_best_csv(resources, preferred_keywords=None):
    """Find best CSV resource, preferring those with keywords or the first CSV found"""
    csvs = [r for r in resources if r["format"] == "CSV"]
    if not csvs:
        # Try other formats
        for fmt in ["XLSX", "XLS"]:
            found = [r for r in resources if r["format"] == fmt]
            if found:
                return found[0], fmt
        return None, None
    
    if preferred_keywords:
        for kw in preferred_keywords:
            for r in csvs:
                if kw.lower() in (r.get("name", "") + r.get("description", "")).lower():
                    return r, "CSV"
    
    return csvs[0], "CSV"

results = {}
seen_ids = set()

for qinfo in queries:
    name = qinfo["name"]
    q = qinfo["q"]
    print(f"\n[{name}] Buscando: '{q}'")
    
    r = requests.get(f"{BASE}/package_search", params={"q": q, "rows": 10}, timeout=20)
    if not r.ok:
        print(f"  ERROR: HTTP {r.status_code}")
        continue
    
    data = r.json()
    if not data.get("success") or not data["result"]["results"]:
        print(f"  No results found")
        continue
    
    # Pick the most relevant result (first one that has CSV)
    chosen = None
    for ds in data["result"]["results"]:
        has_csv = any(res["format"] == "CSV" for res in ds.get("resources", []))
        if has_csv and ds["id"] not in seen_ids:
            chosen = ds
            break
    
    if not chosen:
        # Take first one even without CSV
        chosen = data["result"]["results"][0]
    
    seen_ids.add(chosen["id"])
    
    title = chosen["title"]
    print(f"  Dataset: {title[:80]}")
    
    resources = chosen.get("resources", [])
    best_res, fmt = find_best_csv(resources)
    
    if not best_res:
        print(f"  No downloadable resource found")
        continue
    
    url = best_res["url"]
    print(f"  URL: {url[:100]}...")
    
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"  ERROR download: HTTP {resp.status_code}")
            continue
        
        # Detect encoding
        raw = resp.content
        import chardet
        enc = chardet.detect(raw)["encoding"] or "utf-8"
        text = raw.decode(enc, errors="replace")
        
        # Determine file extension
        ext = ".csv" if fmt == "CSV" else (".xlsx" if fmt == "XLSX" else ".xls")
        filepath = os.path.join(OUT, f"{name}{ext}")
        
        # Write as binary (original bytes)
        with open(filepath, "wb") as f:
            f.write(raw)
        
        lines = text.split("\n")
        print(f"  Guardado: {filepath}")
        print(f"  Encoding: {enc} | Filas: {len(lines)} | Tamaño: {len(raw)} bytes")
        print(f"  Primeras 2 filas:")
        for l in lines[:3]:
            print(f"    {l.strip()[:120]}")
        
        results[name] = {
            "file": filepath,
            "rows": len(lines),
            "encoding": enc,
            "size": len(raw),
            "title": title,
            "format": fmt,
        }
        
    except Exception as e:
        print(f"  ERROR: {e}")

# Summary
print("\n\n" + "=" * 70)
print("RESUMEN DE DESCARGAS")
print("=" * 70)
print(f"{'Dataset':<35} {'Filas':<8} {'Formato':<8} {'Tamaño':<10}")
print("-" * 70)
for name, info in results.items():
    size_kb = info["size"] / 1024
    print(f"{name:<35} {info['rows']:<8} {info['format']:<8} {size_kb:.1f} KB")

print(f"\nTotal datasets descargados: {len(results)}/{len(queries)}")
print(f"Carpeta: {OUT}")
