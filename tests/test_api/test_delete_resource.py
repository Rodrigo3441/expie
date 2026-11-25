from fastapi.testclient import TestClient
from lan_file_manager.file_management.management_operations import FileManagement
from lan_file_manager.api.dependencies import return_file_management
from lan_file_manager.config.config import get_config
from main import app

CHUNK_SIZE = get_config()['default_chunk_size']

def test_delete_file(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    file_path = storage / 'document.txt'
    file_path.write_text('Some content')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.delete(
                '/api/delete',
                params={'path': '/', 'name': 'document.txt'}
            )

        assert response.status_code == 200
        assert not file_path.exists()

        assert response.json() == {
            'success': True,
            'data': None,
            'error': None
        }

    finally:
        app.dependency_overrides.clear()

def test_delete_non_empty_directory(tmp_path):
    storage = tmp_path / 'storage'
    documents = storage / 'documents'
    documents.mkdir(parents=True)

    (documents / 'document.txt').write_text('Some content')
    (documents / 'notes.txt').write_text('Some notes')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.delete(
                '/api/delete',
                params={'path': '/documents'}
            )

        assert response.status_code == 200
        assert not documents.exists()

    finally:
        app.dependency_overrides.clear()


def test_delete_storage_root_forbidden(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    (storage / 'document.txt').write_text('Some content')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.delete(
                '/api/delete',
                params={'path': '/'}
            )

        assert response.status_code == 403
        assert storage.exists()
        assert (storage / 'document.txt').exists()

    finally:
        app.dependency_overrides.clear()
