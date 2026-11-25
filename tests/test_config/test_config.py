import pytest
import yaml

from lan_file_manager.config.config import (
    DEFAULT_CONFIG,
    create_default_config,
    get_config,
    validate_config,
)


def test_create_default_config(tmp_path):
    config_path = tmp_path / "config" / "config.yaml"

    create_default_config(config_path)

    assert config_path.exists()

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    assert config == DEFAULT_CONFIG


def test_get_config_creates_missing_file_and_stops(tmp_path):
    config_path = tmp_path / "config" / "config.yaml"

    with pytest.raises(SystemExit) as exc_info:
        get_config(config_path)

    assert exc_info.value.code == 1
    assert config_path.exists()


def test_get_config_does_not_overwrite_existing_file(tmp_path):
    config_path = tmp_path / "config.yaml"
    original_content = "invalid: config"

    config_path.write_text(original_content)

    with pytest.raises(ValueError):
        get_config(config_path)

    assert config_path.read_text() == original_content


def test_validate_config_accepts_valid_config(tmp_path):
    config = {
        **DEFAULT_CONFIG,
        'default_path': str(tmp_path)
    }

    validate_config(config)


@pytest.mark.parametrize(
    "chunk_size",
    [0, -1, 1.5, "1024", True, False]
)
def test_validate_config_rejects_invalid_chunk_size(chunk_size):
    config = DEFAULT_CONFIG.copy()
    config['default_chunk_size'] = chunk_size

    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize(
    "host",
    ["", "   ", 123, None]
)
def test_validate_config_rejects_invalid_host(host):
    config = {
        **DEFAULT_CONFIG,
        'connection': {
            'host': host,
            'port': 3093
        }
    }

    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize(
    "port",
    [0, -1, 65536, 3.14, "3093", True, False, None]
)
def test_validate_config_rejects_invalid_port(port):
    config = {
        **DEFAULT_CONFIG,
        'connection': {
            'host': 'localhost',
            'port': port
        }
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_validate_config_rejects_missing_connection_host():
    config = {
        **DEFAULT_CONFIG,
        'connection': {'port': 3093}
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_validate_config_rejects_missing_connection_port():
    config = {
        **DEFAULT_CONFIG,
        'connection': {'host': 'localhost'}
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_validate_config_rejects_invalid_connection_type():
    config = {
        **DEFAULT_CONFIG,
        'connection': 'localhost'
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_validate_config_rejects_empty_default_path():
    config = {
        **DEFAULT_CONFIG,
        'default_path': ''
    }

    with pytest.raises(ValueError):
        validate_config(config)
