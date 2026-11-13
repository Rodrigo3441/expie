from src.lan_file_manager.file_management.management_operations import FileManagement
from src.lan_file_manager.config.config import get_config
import pathlib
import pytest

def test_non_existing_directory():
    configuration = get_config()
    operations = FileManagement(pathlib.Path(configuration['default_path']))

    with pytest.raises(OSError):
        results = operations.list_directory('/asdasdasdasd')

def test_directory_name_without_slash():
    configuration = get_config()
    operations = FileManagement(pathlib.Path(configuration['default_path']))

    with pytest.raises(ValueError):
        results = operations.list_directory('sdasdasdasd')


def test_point_to_file(tmp_path):
    operations = FileManagement(tmp_path)

    test_file = tmp_path / 'test.txt'
    test_file.write_text('')

    with pytest.raises(NotADirectoryError):
        results = operations.list_directory('/test.txt')

def test_root_directory(tmp_path):
    operations = FileManagement(tmp_path)

    test_file = tmp_path / 'test.txt'
    test_file.write_text('')

    results = operations.list_directory('/')
    assert results[0]['name'] == 'test.txt'
    assert len(results) == 1

def test_subfolder_directory(tmp_path):
    operations = FileManagement(tmp_path)

    test_folder = tmp_path / 'dir'
    test_folder.mkdir()

    test_file = test_folder / 'test.tmp'
    test_file.write_text('a')

    results = operations.list_directory('/dir')
    assert results[0]['name'] == 'test.tmp'
    assert len(results) == 1

def test_invalid_path(tmp_path):
    operations = FileManagement(tmp_path)

    test_folder = tmp_path / 'dir'
    test_folder.mkdir()

    with pytest.raises(OSError):
        results = operations.list_directory('/../dir')

def test_non_existing_folder(tmp_path):
    operations = FileManagement(tmp_path)

    with pytest.raises(FileNotFoundError):
        results = operations.list_directory('/asdasdasdasd')
