from fastapi.testclient import TestClient
from src.lan_file_manager.file_management.management_operations import FileManagement
from src.lan_file_manager.api.dependencies import return_file_management
from src.lan_file_manager.config.config import get_config
from main import app
import io
import zipfile

CHUNK_SIZE = get_config()['default_chunk_size']

def test_download_file(tmp_path):
    storage = tmp_path / 'storage'
    storage.mkdir()

    file_path = storage / 'hello.txt'
    file_path.write_text('Hello, world!')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.get('/api/download', params={'path': '/hello.txt'})

        assert response.status_code == 200
        assert response.content == b'Hello, world!'
        assert response.headers['content-type'] == 'text/plain'
        assert 'filename="hello.txt"' in response.headers['content-disposition']

    finally:
        app.dependency_overrides.clear()


def test_download_directory_as_zip(tmp_path):
    storage = tmp_path / 'storage'
    documents = storage / 'documents'
    documents.mkdir(parents=True)

    (documents / 'report.txt').write_text('Report content')
    (documents / 'notes.txt').write_text('Notes content')

    file_management = FileManagement(storage, CHUNK_SIZE)
    app.dependency_overrides[return_file_management] = lambda: file_management

    try:
        with TestClient(app) as client:
            response = client.get('/api/download', params={'path': '/documents'})

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/zip'
        assert 'filename="documents.zip"' in response.headers['content-disposition']

        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            assert 'report.txt' in archive.namelist()
            assert 'notes.txt' in archive.namelist()

            assert archive.read('report.txt') == b'Report content'
            assert archive.read('notes.txt') == b'Notes content'

    finally:
        app.dependency_overrides.clear()