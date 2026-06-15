import requests
import pandas as pd
import chardet
import os

BASE_URL = "https://datosabiertos.gob.pa/api/3/action"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
    def save_raw(df, filename, path=None):
        if path is None:
            path = os.path.join(ROOT, "data", "raw")
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, filename)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        return filepath

    def get_resource_modified(self, resource_id):
        """Consulta last_modified de un recurso por su ID."""
        try:
            r = self._session.get(
                f"{self.base_url}/resource_show",
                params={"id": resource_id},
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json()
            if data.get("success"):
                res = data["result"]
                return res.get("last_modified") or res.get("created") or "unknown"
        except Exception:
            pass
        return "unknown"

    def _needs_download(self, name, cfg, raw_path):
        """Verifica si un dataset necesita descargarse comparando last_modified con el archivo local."""
        resource_id = cfg.get("resource_id")
        if not resource_id:
            return True

        filepath = os.path.join(raw_path, f"{name}.csv")
        if not os.path.exists(filepath):
            return True

        remote_modified = self.get_resource_modified(resource_id)
        if remote_modified == "unknown":
            return True

        local_mtime = os.path.getmtime(filepath)
        try:
            from datetime import datetime
            remote_dt = datetime.fromisoformat(remote_modified.replace("Z", "+00:00"))
            remote_ts = remote_dt.timestamp()
            return remote_ts > local_mtime + 60
        except (ValueError, TypeError):
            return True

    def download_all(self, config, force=False):
        results = {}
        raw_path = os.path.join(ROOT, "data", "raw")
        os.makedirs(raw_path, exist_ok=True)

        for name, cfg in config.items():
            if not force and not self._needs_download(name, cfg, raw_path):
                filepath = os.path.join(raw_path, f"{name}.csv")
                print(f"  [{name}] Sin cambios, saltando")
                try:
                    df = pd.read_csv(filepath, encoding="utf-8-sig", low_memory=False)
                    results[name] = {"df": df, "encoding": "utf-8-sig", "separator": ",", "filepath": filepath}
                except Exception:
                    results[name] = None
                continue

            print(f"  [{name}] Buscando: {cfg['query']}")
            resource_id = cfg.get("resource_id")
            if resource_id:
                url = f"{self.base_url}/resource_show"
                r = self._session.get(url, params={"id": resource_id}, timeout=self.timeout)
                if r.ok:
                    data = r.json()
                    if data.get("success"):
                        res = data["result"]
                        csv_url = res.get("url")
                        if csv_url:
                            print(f"    Descargando por resource_id...")
                            df, enc, sep = self.download_csv(csv_url)
                            filename = f"{name}.csv"
                            filepath = self.save_raw(df, filename, path=raw_path)
                            print(f"    -> {len(df)} filas, {df.shape[1]} columnas, encoding={enc}, sep='{sep}'")
                            print(f"    -> Guardado: {filepath}")
                            results[name] = {"df": df, "encoding": enc, "separator": sep, "filepath": filepath}
                            continue

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
            filepath = self.save_raw(df, filename, path=raw_path)
            print(f"    -> {len(df)} filas, {df.shape[1]} columnas, encoding={enc}, sep='{sep}'")
            print(f"    -> Guardado: {filepath}")
            results[name] = {"df": df, "encoding": enc, "separator": sep, "filepath": filepath}
        return results
