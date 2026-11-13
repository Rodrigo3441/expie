from src.lan_file_manager.config.config import get_config
import pathlib
import pytest

def test_get_config():
    test_existing_file = pathlib.Path(__file__).parents[2] / 'config/config.yaml'
    assert get_config(test_existing_file) is not None

def test_get_config_missing_file():
    test_missing_file = pathlib.Path(__file__).parents[2] / 'config/missing_config.yaml'
    
    with pytest.raises(FileNotFoundError):
        get_config(test_missing_file)


def test_get_config_missing_required_fields(tmp_path):
    # Create a temporary config file without required fields
    config_file = tmp_path / "config.yaml"
    config_file.write_text("some_other_field: value")

    with pytest.raises(ValueError):
        get_config(config_file)

def test_get_config_empty_yaml_file(tmp_path):
    # Create a temporary empty config file
    config_file = tmp_path / "config.yaml"
    config_file.write_text("")

    with pytest.raises(ValueError):
        get_config(config_file)

def test_get_config_invalid_default_path(tmp_path):
    # Create a temporary config file with an invalid default path
    config_file = tmp_path / "config.yaml"
    config_file.write_text("default_path: /invalid/path\nconnection: some_connection")

    with pytest.raises(ValueError):
        get_config(config_file)

def test_get_config_is_the_config_file(tmp_path):
    # Create a temporary config file with valid fields
    config_file = tmp_path / "config.yaml"
    config_file.write_text("default_path: .\nconnection: some_connection")

    config = get_config(config_file)
    assert isinstance(config, dict)
    assert 'default_path' in config
    assert 'connection' in config