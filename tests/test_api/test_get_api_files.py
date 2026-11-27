import main
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def storage_path(tmp_path):
    storage = tmp_path / "storage"
    storage.mkdir()
    return storage


@pytest.fixture
def client(storage_path, monkeypatch):
    config = {
        "default_path": str(storage_path),
        "default_chunk_size": 1048576,
        "connection": {
            "host": "localhost",
            "port": 3093
        }
    }

    monkeypatch.setattr(main, "get_config", lambda config_path: config)

    with TestClient(main.app) as test_client:
        yield test_client


def test_default_endpoint(client):
    response = client.get("/api/contents")

    assert response.status_code == 200


def test_non_existing_directory(client):
    response = client.get("/api/contents?path=/non_existing")

    assert response.status_code == 404


def test_non_allowed_directory(client, tmp_path):
    outside_directory = tmp_path / "outside"
    outside_directory.mkdir()

    response = client.get("/api/contents?path=/../outside")

    assert response.status_code == 403


def test_not_a_directory(client, storage_path):
    test_file = storage_path / "test.txt"
    test_file.write_text("Test content")

    response = client.get("/api/contents?path=/test.txt")

    assert response.status_code == 400