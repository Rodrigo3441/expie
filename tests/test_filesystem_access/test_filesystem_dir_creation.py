from src.lan_file_manager.filesystem_access.directory_operations import create_directory

def test_dir_creation(tmp_path):
    base_folder = tmp_path
    create_directory(base_folder / 'txt/test/temp')

    assert (base_folder / 'txt/test/temp').is_dir()
