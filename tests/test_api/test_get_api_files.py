from fastapi.testclient import TestClient
from main import app

def test_default_endpoint():
    with TestClient(app) as client:
        response = client.get('/api/contents')
        assert response.status_code == 200


def test_non_existing_directory():
    with TestClient(app) as client:
        response = client.get('/api/contents?path=/errro')
        assert response.status_code == 404


def test_non_allowed_directory():
    with TestClient(app) as client:
        response = client.get('/api/contents?path=/../../temp')
        assert response.status_code == 403


def test_not_a_directory():
    with TestClient(app) as client:
        response = client.get('/api/contents?path=/temp/1.jfif')
        assert response.status_code == 400