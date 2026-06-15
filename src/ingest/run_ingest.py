from src.ingest.ckan_client import CkanClient
from src.ingest.datasets_config import DATASETS_CONFIG


def run():
    client = CkanClient()
    print("=" * 60)
    print("INICIANDO DESCARGA DE DATASETS CKAN")
    print("=" * 60)
    results = client.download_all(DATASETS_CONFIG)
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    ok = 0
    fail = 0
    for name, result in results.items():
        if result is None:
            print(f"  X {name}: fallo")
            fail += 1
        else:
            print(f"  OK {name}: {len(result['df'])} filas -> {result['filepath']}")
            ok += 1
    print(f"\n{ok} descargados, {fail} fallidos")


if __name__ == "__main__":
    run()
