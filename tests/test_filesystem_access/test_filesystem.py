import pathlib
import pytest
from src.lan_file_manager.filesystem_access.directory_operations import list_directory

def test_list_directory(tmp_path):
    # Create a temporary config file with an invalid default path
    config_file = tmp_path / "config.yaml"
    config_file.write_text("")

    metadata = list_directory(tmp_path)
    assert metadata[0]['name'] == 'config.yaml'
    assert metadata[0]['name'] != 'cnfig.yaml'

def test_list_directory_empty_folder(tmp_path):
    files = list_directory(tmp_path)
    assert files == []

def test_list_directory_containing_subdirectories(tmp_path):
    testfile1 = tmp_path / 'config.yaml'
    testfile1.write_text('')

    files = list_directory(tmp_path)
    assert files[0]['name'] == 'config.yaml'

    subdir1 = tmp_path / 'temp1'
    subdir1.mkdir()
    files = list_directory(tmp_path)
    assert files[1]['name'] == 'temp1'


    subdir2 = tmp_path / 'temp2'
    subdir2.mkdir()
    files = list_directory(tmp_path)
    assert files[2]['name'] == 'temp2'

    
    assert len(files) == 3
    assert files[0]['type'] == 'FILE'
    assert files[1]['type'] == 'DIRECTORY'
    assert files[2]['type'] == 'DIRECTORY'


def test_list_directory_non_existing_directory():
    with pytest.raises(FileNotFoundError):
        files = list_directory(pathlib.Path('invalidfolder'))


def test_list_directory_point_file(tmp_path):
    testfile1 = tmp_path / 'config.yaml'
    testfile1.write_text('')

    with pytest.raises(NotADirectoryError):
        files = list_directory(testfile1)


def test_list_directory(tmp_path):
    # Create a temporary config file with an invalid default path
    config_file = tmp_path / "config.yaml"
    config_file.write_text("")

    metadata = list_directory(tmp_path)
    assert metadata[0]['extension'] == '.yaml'




