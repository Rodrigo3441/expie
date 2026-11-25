from fastapi.testclient import TestClient
from src.lan_file_manager.file_management.management_operations import FileManagement
from src.lan_file_manager.api.dependencies import return_file_management
from main import app
import pytest
from src.lan_file_manager.config.config import get_config

CHUNK_SIZE = get_config()['default_chunk_size']

def test_create_directory(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.post(
                '/api/create',
                params={'name': 'documents', 'path': '/'}
            )

        assert response.status_code == 200
        assert (storage / 'documents').is_dir()

        assert response.json() == {
            'success': True,
            'data': None,
            'error': None
        }

    finally:
        app.dependency_overrides.clear()


def test_create_existing_directory_fails(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()
    (storage / 'documents').mkdir()

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                '/api/create',
                params={'name': 'documents', 'path': '/'}
            )

        assert response.status_code == 400

    finally:
        app.dependency_overrides.clear()



@pytest.mark.parametrize('name', [
    '',
    '.',
    '..',
    'documents/reports',
    r'documents\reports'
])
def test_create_directory_with_invalid_name(tmp_path, name):
    storage = tmp_path / 'storage'
    storage.mkdir()

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                '/api/create',
                params={'name': name, 'path': '/'}
            )

        assert response.status_code == 400

    finally:
        app.dependency_overrides.clear()