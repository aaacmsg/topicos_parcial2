import pytest
import pandas as pd
import requests
from unittest.mock import patch, MagicMock
from src.ingest.ckan_client import CkanClient


@pytest.fixture
def client():
    return CkanClient(base_url="https://fake-ckan.test/api/3/action")


class TestCkanClient:
    def test_search_datasets_success(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "results": [
                    {"id": "123", "title": "Test Dataset", "resources": []}
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        with patch.object(client._session, "get", return_value=mock_response):
            results = client.search_datasets("test query")
        assert len(results) == 1
        assert results[0]["title"] == "Test Dataset"

    def test_search_datasets_no_results(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": {"results": []}}
        mock_response.raise_for_status = MagicMock()
        with patch.object(client._session, "get", return_value=mock_response):
            results = client.search_datasets("no results")
        assert results == []

    def test_get_csv_resources_filters(self, client):
        dataset = {
            "resources": [
                {"format": "CSV", "url": "http://example.com/data.csv"},
                {"format": "PDF", "url": "http://example.com/doc.pdf"},
                {"format": "XLSX", "url": "http://example.com/data.xlsx"},
            ]
        }
        csvs = CkanClient.get_csv_resources(dataset)
        assert len(csvs) == 1
        assert csvs[0]["format"] == "CSV"

    def test_detect_encoding_latin(self, client):
        content = "Año;Mes;Valor".encode("latin-1")
        encoding = CkanClient._detect_encoding(content)
        assert encoding is not None

    def test_save_raw(self, client, tmp_path):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        path = tmp_path / "raw"
        filepath = CkanClient.save_raw(df, "test.csv", str(path))
        assert pd.read_csv(filepath).shape == (2, 2)

    def test_download_csv_success(self, client):
        csv_content = "a,b\n1,2\n3,4"
        mock_response = MagicMock()
        mock_response.content = csv_content.encode("utf-8")
        mock_response.raise_for_status = MagicMock()
        with patch.object(client._session, "get", return_value=mock_response):
            df, enc, sep = client.download_csv("http://example.com/test.csv")
        assert df.shape == (2, 2)
        assert list(df.columns) == ["a", "b"]

    def test_download_csv_semicolon(self, client):
        csv_content = "a;b\n1;2\n3;4"
        mock_response = MagicMock()
        mock_response.content = csv_content.encode("utf-8")
        mock_response.raise_for_status = MagicMock()
        with patch.object(client._session, "get", return_value=mock_response):
            df, enc, sep = client.download_csv("http://example.com/test.csv")
        assert df.shape == (2, 2)
        assert sep == ";"

    def test_download_all_with_config(self, client):
        mock_search = MagicMock(return_value=[
            {"id": "1", "title": "D1", "resources": [
                {"format": "CSV", "url": "http://example.com/d1.csv"}
            ]}
        ])
        mock_csv = MagicMock(return_value=(pd.DataFrame({"x": [1]}), "utf-8", ","))
        mock_save = MagicMock(return_value="data/raw/d1.csv")
        client.search_datasets = mock_search
        client.download_csv = mock_csv
        client.save_raw = mock_save

        config = {"d1": {"query": "test", "rows": 5, "resource_index": 0}}
        results = client.download_all(config)
        assert results["d1"] is not None
        assert len(results["d1"]["df"]) == 1
