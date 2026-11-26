from fastapi.testclient import TestClient
from lan_file_manager.file_management.management_operations import FileManagement
from lan_file_manager.api.dependencies import return_file_management
from main import app

CHUNK_SIZE = 1048576

def test_move_file(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    source_dir = storage / 'documents'
    destination_dir = storage / 'backups'

    source_dir.mkdir()
    destination_dir.mkdir()

    source_file = source_dir / 'report.txt'
    source_file.write_text('Hello, world!')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.patch(
                '/api/move',
                params={
                    'source_path': '/documents/report.txt',
                    'destination_path': '/backups'
                }
            )

        moved_file = destination_dir / 'report.txt'

        assert response.status_code == 200
        assert response.json()['success'] is True
        assert moved_file.exists()
        assert not source_file.exists()
        assert moved_file.read_text() == 'Hello, world!'

    finally:
        app.dependency_overrides.clear()


def test_move_directory(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    source_dir = storage / 'documents'
    destination_dir = storage / 'backups'

    source_dir.mkdir()
    destination_dir.mkdir()

    (source_dir / 'report.txt').write_text('Hello, world!')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.patch(
                '/api/move',
                params={
                    'source_path': '/documents',
                    'destination_path': '/backups'
                }
            )

        moved_dir = destination_dir / 'documents'

        assert response.status_code == 200
        assert response.json()['success'] is True
        assert moved_dir.is_dir()
        assert not source_dir.exists()
        assert (moved_dir / 'report.txt').read_text() == 'Hello, world!'

    finally:
        app.dependency_overrides.clear()


def test_move_directory_into_its_subdirectory(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    source_dir = storage / 'documents'
    destination_dir = source_dir / 'backups'

    destination_dir.mkdir(parents=True)
    (source_dir / 'report.txt').write_text('Hello, world!')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.patch(
                '/api/move',
                params={
                    'source_path': '/documents',
                    'destination_path': '/documents/backups'
                }
            )

        assert response.status_code == 400
        assert source_dir.is_dir()
        assert destination_dir.is_dir()
        assert (source_dir / 'report.txt').exists()

    finally:
        app.dependency_overrides.clear()