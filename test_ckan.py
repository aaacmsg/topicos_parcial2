import requests, json

print("=== PROBANDO CKAN DATOS ABIERTOS PANAMA ===\n")

# 1. Probar que el portal existe
r = requests.get("https://datosabiertos.gob.pa/api/3/action/site_read", timeout=15)
print(f"1. Portal responde: {r.status_code}")
print(f"   Respuesta: {r.text[:100]}\n")

# 2. Buscar datasets económicos
r2 = requests.get(
    "https://datosabiertos.gob.pa/api/3/action/package_search",
    params={"q": "economia", "rows": 5},
    timeout=15,
)
data2 = r2.json()
print(f'2. Busqueda "economia": {data2.get("success")}')
print(f'   Total resultados: {data2["result"]["count"]}')
if data2["result"]["results"]:
    for ds in data2["result"]["results"][:3]:
        print(f'   - {ds["title"]}')
        org = ds.get("organization", {})
        if org:
            print(f'     Organizacion: {org.get("title", "N/A")}')
        for rec in ds.get("resources", [])[:2]:
            print(f'     [{rec["format"]}] {rec["url"][:120]}')

print()

# 3. Datasets del INEC
r3 = requests.get(
    "https://datosabiertos.gob.pa/api/3/action/package_search",
    params={"q": "INEC", "rows": 5},
    timeout=15,
)
data3 = r3.json()
print(f'3. Datasets del INEC: {data3["result"]["count"]} resultados')
if data3["result"]["results"]:
    for ds in data3["result"]["results"][:3]:
        print(f'   - {ds["title"]}')

print()

# 4. Listar organizaciones
r4 = requests.get(
    "https://datosabiertos.gob.pa/api/3/action/organization_list",
    params={"all_fields": True},
    timeout=15,
)
data4 = r4.json()
print(f"4. Organizaciones publicando datos: {len(data4['result'])}")
for org in data4["result"][:10]:
    print(f"   - {org['title']} ({org['name']})")
