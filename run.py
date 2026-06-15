"""
Entry point unico para el proyecto.
Uso:
  python run.py              # Pipeline inteligente + dashboard (solo descarga cambios)
  python run.py --force      # Forzar redescarga de TODO
  python run.py --dashboard  # Solo dashboard (datos ya procesados)
  python run.py --ingest     # Solo descarga inteligente
  python run.py --help       # Ayuda
"""
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

VENV_PYTHON = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
if not sys.prefix.endswith(".venv") and os.path.exists(VENV_PYTHON):
    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

import subprocess
import argparse
sys.path.insert(0, ROOT)


def run_cmd(cmd, desc):
    print(f"\n{'=' * 60}")
    print(f"  {desc}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd, shell=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"  ERROR: {desc} fallo con codigo {result.returncode}")
        sys.exit(result.returncode)
    print()


def run_ingest(force=False):
    ingest_code = (
        "from src.ingest.ckan_client import CkanClient;"
        "from src.ingest.datasets_config import DATASETS_CONFIG;"
        f"client = CkanClient(); client.download_all(DATASETS_CONFIG, force={'True' if force else 'False'})"
    )
    desc = "FORZANDO REDESCARGA DE DATOS DESDE CKAN" if force else "DESCARGANDO DATOS DESDE CKAN (solo cambios)"
    run_cmd(f"{sys.executable} -c \"{ingest_code}\"", desc)


def main():
    parser = argparse.ArgumentParser(description="Dashboard Indicadores Economicos Panama")
    parser.add_argument("--dashboard", action="store_true", help="Solo iniciar dashboard")
    parser.add_argument("--ingest", action="store_true", help="Solo descargar datos (inteligente)")
    parser.add_argument("--force", action="store_true", help="Forzar redescarga de todos los datasets")
    parser.add_argument("--preprocess", action="store_true", help="Solo preprocesar")
    parser.add_argument("--train", action="store_true", help="Solo entrenar modelos")
    parser.add_argument("--skip-download", action="store_true", help="Saltar descarga")
    args = parser.parse_args()

    python = sys.executable

    if args.dashboard:
        run_cmd(f"{python} -m streamlit run src/dashboard/app.py", "INICIANDO DASHBOARD")
        return

    if args.ingest:
        run_ingest(force=args.force)
        return

    if args.preprocess:
        run_cmd(f"{python} -m src.preprocessing.run_preprocessing", "PREPROCESANDO DATOS")
        return

    if args.train:
        run_cmd(f"{python} -c \"from src.models.prophet_model import entrenar_completo; entrenar_completo()\"",
                "ENTRENANDO PROPHET (IMAE)")
        run_cmd(f"{python} -c \"from src.models.arima_model import entrenar_completo; entrenar_completo()\"",
                "ENTRENANDO ARIMA (PIB)")
        return

    if not args.skip_download:
        run_ingest(force=args.force)

    run_cmd(f"{python} -m src.preprocessing.run_preprocessing", "PREPROCESANDO DATOS")

    run_cmd(f"{python} -c \"from src.models.prophet_model import entrenar_completo; entrenar_completo()\"",
            "ENTRENANDO PROPHET (IMAE)")
    run_cmd(f"{python} -c \"from src.models.arima_model import entrenar_completo; entrenar_completo()\"",
            "ENTRENANDO ARIMA (PIB)")

    run_cmd(f"{python} -m streamlit run src/dashboard/app.py", "INICIANDO DASHBOARD")


if __name__ == "__main__":
    main()
