import io
import pathlib
import pytest
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from threading import Barrier
from lan_file_manager.file_management.management_operations import FileManagement
from lan_file_manager.filesystem_access import directory_operations as filesystem_access

CHUNK_SIZE = 1024 * 1024

def test_upload_replaces_existing_file(tmp_path):
    # Arrange
    existing_file = tmp_path / "example.txt"
    existing_file.write_text("old content")

    file_management = FileManagement(tmp_path, CHUNK_SIZE)

    uploaded_content = b"new content"
    file_stream = io.BytesIO(uploaded_content)

    # Act
    file_management.upload_file(
        file_stream=file_stream,
        destination_dir="/",
        filename="example.txt"
    )

    # Assert
    assert existing_file.exists()
    assert existing_file.read_bytes() == uploaded_content



def test_interrupted_upload_cleans_temp_file(tmp_path, monkeypatch):
    # Arrange
    existing_file = tmp_path / "example.txt"
    existing_file.write_text("old content")

    file_management = FileManagement(tmp_path, CHUNK_SIZE)

    uploaded_content = b"x" * (CHUNK_SIZE + 1)
    file_stream = io.BytesIO(uploaded_content)

    created_temp_files = []
    original_create_temp_file = filesystem_access.create_temp_file
    original_write = filesystem_access.write_to_temp_file

    def track_temp_file(destination_dir):
        temp_path = original_create_temp_file(destination_dir)
        created_temp_files.append(temp_path)
        return temp_path

    write_count = 0

    def fail_on_second_write(temp_path, chunk):
        nonlocal write_count
        write_count += 1

        if write_count == 2:
            raise OSError("Simulated upload interruption")

        original_write(temp_path, chunk)

    monkeypatch.setattr(
        filesystem_access, "create_temp_file", track_temp_file
    )
    monkeypatch.setattr(
        filesystem_access, "write_to_temp_file", fail_on_second_write
    )

    # Act & Assert
    with pytest.raises(OSError, match="Simulated upload interruption"):
        file_management.upload_file(
            file_stream=file_stream,
            destination_dir="/",
            filename="example.txt"
        )

    # Verify cleanup and preservation
    assert len(created_temp_files) == 1
    assert not created_temp_files[0].exists()
    assert existing_file.read_text() == "old content"


def test_concurrent_uploads_different_files(tmp_path):
    file_management = FileManagement(tmp_path, CHUNK_SIZE)

    barrier = Barrier(2)

    class SynchronizedStream(io.BytesIO):
        def read(self, size=-1):
            if not hasattr(self, "started"):
                self.started = True
                barrier.wait(timeout=5)

            return super().read(size)

    content_a = b"Content of file A"
    content_b = b"Content of file B"

    stream_a = SynchronizedStream(content_a)
    stream_b = SynchronizedStream(content_b)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(
            file_management.upload_file,
            stream_a, "/", "file_a.txt"
        )

        future_b = executor.submit(
            file_management.upload_file,
            stream_b, "/", "file_b.txt"
        )

        future_a.result()
        future_b.result()

    # Verify both uploads
    assert (tmp_path / "file_a.txt").read_bytes() == content_a
    assert (tmp_path / "file_b.txt").read_bytes() == content_b


def test_concurrent_uploads_same_filename(tmp_path):
    file_management = FileManagement(tmp_path, CHUNK_SIZE)

    barrier = Barrier(2)

    class SynchronizedStream(io.BytesIO):
        def read(self, size=-1):
            if not hasattr(self, "started"):
                self.started = True
                barrier.wait(timeout=5)

            return super().read(size)

    content_a = b"A" * 1024
    content_b = b"B" * 1024

    stream_a = SynchronizedStream(content_a)
    stream_b = SynchronizedStream(content_b)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(
            file_management.upload_file,
            stream_a, "/", "example.txt"
        )

        future_b = executor.submit(
            file_management.upload_file,
            stream_b, "/", "example.txt"
        )

        future_a.result()
        future_b.result()

    # The destination must contain one complete upload.
    final_file = tmp_path / "example.txt"

    assert final_file.exists()
    assert final_file.read_bytes() in (content_a, content_b)
