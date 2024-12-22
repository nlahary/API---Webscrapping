import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
from pathlib import Path
import json

MOCKED_CONFIG_FILE = {
    "test1": {
        "name": "test1",
        "url": "https://test1.fr/"
    },
    "test2": {
        "name": "test2",
        "url": "https://test2.fr/"
    }
}


class TestDataRoute:

    @pytest.fixture
    def client(self) -> TestClient:
        """
        Test client for integration tests
        """
        from main import get_application

        app = get_application()
        return TestClient(app, base_url="http://testserver")

    @pytest.fixture
    def mocked_configs_file(self, tmp_path: Path) -> Path:
        json_file = tmp_path / "mocked_urls_config.json"
        with open(json_file, "w") as file:
            json.dump(MOCKED_CONFIG_FILE, file)
        return json_file

    def test_get_dataset_200(self, client, mocked_configs_file):
        with patch("src.services.data.JSON_CONFIG_PATH", new=mocked_configs_file):
            response = client.get("/dataset/test1")
            assert response.status_code == 200
            assert response.json() == MOCKED_CONFIG_FILE["test1"]

    def test_get_dataset_404(self, client, mocked_configs_file):
        with patch("src.services.data.JSON_CONFIG_PATH", new=mocked_configs_file):
            response = client.get("/dataset/test3")
            assert response.status_code == 404
            assert response.json() == {
                "detail": "Dataset not found in configuration file: test3"}

    def test_post_dataset_201(self, client, mocked_configs_file):
        with patch("src.services.data.JSON_CONFIG_PATH", new=mocked_configs_file):
            response = client.post("/dataset", json={
                "name": "test3",
                "url": "https://test3.fr/"
            })
            assert response.status_code == 201
            assert response.json() == {
                "name": "test3",
                "url": "https://test3.fr/"
            }

    def test_post_dataset_403(self, client, mocked_configs_file):
        with patch("src.services.data.JSON_CONFIG_PATH", new=mocked_configs_file):
            response = client.post("/dataset", json={
                "name": "test1",
                "url": "https://test3.fr/"
            })
            assert response.status_code == 403
            assert response.json() == {
                "detail": "Dataset already exists: test1. Use PUT if you wish to update it."}

    def test_post_dataset_500(self, client, mocked_configs_file):
        mock_file = mock_open()
        mock_file.side_effect = FileNotFoundError()

        with patch("src.services.data.JSON_CONFIG_PATH", new=mocked_configs_file):
            with patch("builtins.open", mock_file):
                response = client.post("/dataset", json={
                    "name": "test4",
                    "url": "https://test4.fr/"
                })
                assert response.status_code == 500
                assert response.json() == {
                    "detail": f"Configuration file not found: {mocked_configs_file}"
                }

    def test_put_dataset_200(self, client, mocked_configs_file):
        with patch("src.services.data.JSON_CONFIG_PATH", new=mocked_configs_file):
            response = client.put("/dataset", json={
                "name": "test1",
                "url": "https://test3.fr/"
            })
            assert response.status_code == 200
            assert response.json() == {
                "name": "test1",
                "url": "https://test3.fr/"
            }

    def test_put_dataset_201(self, client, mocked_configs_file):
        with patch("src.services.data.JSON_CONFIG_PATH", new=mocked_configs_file):
            response = client.put("/dataset", json={
                "name": "test3",
                "url": "https://test3.fr/"
            })
            assert response.status_code == 201
            assert response.json() == {
                "name": "test3",
                "url": "https://test3.fr/"
            }
