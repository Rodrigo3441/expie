from lan_file_manager.file_management.management_operations import FileManagement
import pathlib
import pytest

CHUNK_SIZE = 1048576

def create_operations(path: pathlib.Path) -> FileManagement:
    return FileManagement(path, CHUNK_SIZE)


def test_non_existing_directory(tmp_path):
    operations = create_operations(tmp_path)

    with pytest.raises(OSError):
        operations.list_directory('/asdasdasdasd')


def test_directory_name_without_slash(tmp_path):
    operations = create_operations(tmp_path)

    with pytest.raises(ValueError):
        operations.list_directory('sdasdasdasd')


def test_point_to_file(tmp_path):
    operations = create_operations(tmp_path)

    test_file = tmp_path / 'test.txt'
    test_file.write_text('')

    with pytest.raises(NotADirectoryError):
        operations.list_directory('/test.txt')


def test_root_directory(tmp_path):
    operations = create_operations(tmp_path)

    test_file = tmp_path / 'test.txt'
    test_file.write_text('')

    results = operations.list_directory('/')

    assert results[0]['name'] == 'test.txt'
    assert len(results) == 1


def test_subfolder_directory(tmp_path):
    operations = create_operations(tmp_path)

    test_folder = tmp_path / 'dir'
    test_folder.mkdir()

    test_file = test_folder / 'test.tmp'
    test_file.write_text('a')

    results = operations.list_directory('/dir')

    assert results[0]['name'] == 'test.tmp'
    assert len(results) == 1


def test_invalid_path(tmp_path):
    operations = create_operations(tmp_path)

    test_folder = tmp_path / 'dir'
    test_folder.mkdir()

    with pytest.raises(PermissionError):
        operations.list_directory('/../dir')


def test_non_existing_folder(tmp_path):
    operations = create_operations(tmp_path)

    with pytest.raises(FileNotFoundError):
        operations.list_directory('/asdasdasdasd')
