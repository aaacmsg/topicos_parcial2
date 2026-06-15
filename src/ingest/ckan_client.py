import requests
import pandas as pd
import chardet
import os
from pathlib import Path

BASE_URL = "https://datosabiertos.gob.pa/api/3/action"


class CkanClient:
    def __init__(self, base_url=BASE_URL, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    def search_datasets(self, query, rows=10):
        r = self._session.get(
            f"{self.base_url}/package_search",
            params={"q": query, "rows": rows},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("success"):
            return []
        return data["result"]["results"]

    def get_dataset(self, dataset_id):
        r = self._session.get(
            f"{self.base_url}/package_show",
            params={"id": dataset_id},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("result")

    @staticmethod
    def get_csv_resources(dataset):
        return [r for r in dataset.get("resources", []) if r.get("format", "").upper() == "CSV"]

    @staticmethod
    def _detect_encoding(content: bytes) -> str:
        result = chardet.detect(content)
        enc = result.get("encoding") or "utf-8"
        if enc.lower() in ("ascii", "utf-8"):
            return "utf-8"
        return enc

    def _try_read_csv(self, url, encoding):
        raw = self._session.get(url, timeout=self.timeout).content
        detected = self._detect_encoding(raw)
        text = raw.decode(detected, errors="replace")
        for sep in [",", ";"]:
            try:
                import io
                df = pd.read_csv(io.StringIO(text), sep=sep, encoding="utf-8")
                if df.shape[1] > 1:
                    return df, detected, sep
            except Exception:
                continue
        df = pd.read_csv(io.StringIO(text), sep=",", encoding="utf-8")
        return df, detected, ","

    def download_csv(self, url):
        raw = self._session.get(url, timeout=self.timeout).content
        detected = self._detect_encoding(raw)
        text = raw.decode(detected, errors="replace")
        import io
        for sep in [",", ";"]:
            try:
                df = pd.read_csv(io.StringIO(text), sep=sep, encoding="utf-8")
                if df.shape[1] > 1:
                    return df, detected, sep
            except Exception:
                continue
        df = pd.read_csv(io.StringIO(text), sep=",", encoding="utf-8")
        return df, detected, ","

    @staticmethod
    def save_raw(df, filename, path="data/raw"):
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, filename)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        return filepath

    def download_all(self, config):
        results = {}
        for name, cfg in config.items():
            print(f"  [{name}] Buscando: {cfg['query']}")
            datasets = self.search_datasets(cfg["query"], rows=cfg.get("rows", 5))
            if not datasets:
                print(f"    No se encontraron resultados")
                results[name] = None
                continue
            dataset = datasets[0]
            csvs = self.get_csv_resources(dataset)
            if not csvs:
                print(f"    No tiene recursos CSV")
                results[name] = None
                continue
            idx = cfg.get("resource_index", 0)
            if idx >= len(csvs):
                idx = 0
            url = csvs[idx]["url"]
            print(f"    Descargando: {url[:80]}...")
            df, enc, sep = self.download_csv(url)
            filename = f"{name}.csv"
            filepath = self.save_raw(df, filename, path=cfg.get("output_path", "data/raw"))
            print(f"    -> {len(df)} filas, {df.shape[1]} columnas, encoding={enc}, sep='{sep}'")
            print(f"    -> Guardado: {filepath}")
            results[name] = {"df": df, "encoding": enc, "separator": sep, "filepath": filepath}
        return results
