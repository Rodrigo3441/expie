from fastapi.testclient import TestClient
from src.lan_file_manager.file_management.management_operations import FileManagement
from src.lan_file_manager.api.dependencies import return_file_management
from src.lan_file_manager.config.config import get_config
from main import app

CHUNK_SIZE = get_config()['default_chunk_size']

def test_rename_file(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    old_file = storage / 'old.txt'
    old_file.write_text('Hello, world!')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.patch(
                '/api/rename',
                params={
                    'path': '/',
                    'old_name': 'old.txt',
                    'new_name': 'new.txt'
                }
            )

        assert response.status_code == 200
        assert (storage / 'new.txt').exists()
        assert not old_file.exists()
        assert (storage / 'new.txt').read_text() == 'Hello, world!'

    finally:
        app.dependency_overrides.clear()


def test_rename_directory(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    old_directory = storage / 'old_folder'
    old_directory.mkdir()
    (old_directory / 'hello.txt').write_text('Hello, world!')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.patch(
                '/api/rename',
                params={
                    'path': '/',
                    'old_name': 'old_folder',
                    'new_name': 'new_folder'
                }
            )

        new_directory = storage / 'new_folder'

        assert response.status_code == 200
        assert new_directory.is_dir()
        assert not old_directory.exists()
        assert (new_directory / 'hello.txt').read_text() == 'Hello, world!'

    finally:
        app.dependency_overrides.clear()


def test_rename_resource_destination_already_exists(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    old_file = storage / 'old.txt'
    existing_file = storage / 'existing.txt'

    old_file.write_text('Original content')
    existing_file.write_text('Existing content')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.patch(
                '/api/rename',
                params={
                    'path': '/',
                    'old_name': 'old.txt',
                    'new_name': 'existing.txt'
                }
            )

        assert response.status_code == 400
        assert old_file.exists()
        assert existing_file.exists()
        assert old_file.read_text() == 'Original content'
        assert existing_file.read_text() == 'Existing content'

    finally:
        app.dependency_overrides.clear()