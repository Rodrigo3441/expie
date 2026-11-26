from fastapi.testclient import TestClient
from lan_file_manager.file_management.management_operations import FileManagement
from lan_file_manager.api.dependencies import return_file_management
from lan_file_manager.filesystem_access import directory_operations as filesystem_access
from main import app
import pytest

CHUNK_SIZE = 1048576

def test_upload_file(tmp_path):
    file_management = FileManagement(tmp_path, CHUNK_SIZE)

    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.post(
                '/api/upload?path=/',
                files={
                    'file': ('hello.txt', b'Hello world!', 'text/plain')
                }
            )

            assert response.status_code == 200
            assert response.json()['success'] is True

            uploaded_file = tmp_path / 'hello.txt'

            assert uploaded_file.exists()
            assert uploaded_file.read_bytes() == b'Hello world!'

    finally:
        app.dependency_overrides.clear()


def test_upload_failure_preserves_existing_file(tmp_path, monkeypatch):
    existing_file = tmp_path / 'example.txt'
    existing_file.write_bytes(b'original content')

    file_management = FileManagement(tmp_path, CHUNK_SIZE)

    app.dependency_overrides[return_file_management] = lambda: file_management

    def simulate_write_failure(temp_path, chunk):
        raise OSError('Simulated disk failure')

    monkeypatch.setattr(
        filesystem_access,
        'write_to_temp_file',
        simulate_write_failure
    )

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                '/api/upload?path=/',
                files={
                    'file': ('example.txt', b'new content', 'text/plain')
                }
            )

        assert response.status_code == 400

        assert existing_file.read_bytes() == b'original content'

        remaining_files = list(tmp_path.iterdir())

        assert remaining_files == [existing_file]

    finally:
        app.dependency_overrides.clear()

def test_upload_replaces_existing_file(tmp_path):
    existing_file = tmp_path / 'example.txt'
    existing_file.write_bytes(b'original content')

    file_management = FileManagement(tmp_path, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.post(
                '/api/upload?path=/',
                files={
                    'file': ('example.txt', b'new content', 'text/plain')
                }
            )

        assert response.status_code == 200
        assert response.json()['success'] is True

        assert existing_file.exists()
        assert existing_file.read_bytes() == b'new content'

        assert list(tmp_path.iterdir()) == [existing_file]

    finally:
        app.dependency_overrides.clear()


def test_upload_creates_nonexistent_directory(tmp_path):
    file_management = FileManagement(tmp_path, CHUNK_SIZE)

    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.post(
                '/api/upload?path=/nonexistent',
                files={
                    'file': ('example.txt', b'Hello world!', 'text/plain')
                }
            )

        assert response.status_code == 200
        assert response.json()['success'] is True

        uploaded_file = tmp_path / 'nonexistent' / 'example.txt'

        assert uploaded_file.exists()
        assert uploaded_file.read_bytes() == b'Hello world!'

    finally:
        app.dependency_overrides.clear()


def test_upload_to_file_instead_of_directory(tmp_path):
    existing_file = tmp_path / 'documents'
    existing_file.write_bytes(b'original content')

    file_management = FileManagement(tmp_path, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.post(
                '/api/upload?path=/documents',
                files={
                    'file': ('example.txt', b'new content', 'text/plain')
                }
            )

        assert response.status_code == 400

        body = response.json()

        assert body['success'] is False
        assert body['data'] is None
        assert body['error']['code'] == 'NOT_A_DIRECTORY'

        assert existing_file.read_bytes() == b'original content'

    finally:
        app.dependency_overrides.clear()


import pytest


@pytest.mark.parametrize(
    'filename',
    [
        'folder/example.txt',
        r'folder\example.txt',
    ]
)
def test_upload_with_invalid_filename(tmp_path, filename):
    file_management = FileManagement(tmp_path, CHUNK_SIZE)

    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                '/api/upload?path=/',
                files={
                    'file': (filename, b'Hello world!', 'text/plain')
                }
            )

        assert response.status_code == 400

        body = response.json()

        assert body['success'] is False
        assert body['data'] is None
        assert body['error']['code'] == 'INVALID_VALUE'

    finally:
        app.dependency_overrides.clear()