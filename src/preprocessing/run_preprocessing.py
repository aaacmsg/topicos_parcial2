from src.preprocessing.pipeline import run_pipeline

if __name__ == "__main__":
    print("=" * 60)
    print("PIPELINE DE PREPROCESAMIENTO")
    print("=" * 60)
    results = run_pipeline()
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    ok = sum(1 for v in results.values() if v is not None)
    fail = sum(1 for v in results.values() if v is None)
    print(f"{ok} procesados, {fail} fallidos/omitidos")
