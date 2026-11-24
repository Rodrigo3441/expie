import yaml
import pathlib

DEFAULT_CONFIG_PATH = pathlib.Path(__file__).parents[3] / 'config/config.yaml'

DEFAULT_CONFIG_KEYS = {
    'default_path', 
    'default_chunk_size', 
    'connection'
}

DEFAULT_CONFIG = {
    'default_path': '',
    'default_chunk_size': 1048576,
    'connection': {
        'host': 'localhost',
        'port': 3093
    }
}

def create_default_config(config_path: pathlib.Path) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as config_file:
        yaml.safe_dump(DEFAULT_CONFIG, config_file, sort_keys=False)

    print(
        f"Configuration file created at: {config_path}\n"
        "Please review and configure the file before starting Expie again."
    )

def validate_config(config: dict) -> None:
    missing_keys = DEFAULT_CONFIG_KEYS - config.keys()

    if missing_keys:
        raise ValueError(
            f"Config file is missing required fields: {', '.join(sorted(missing_keys))}"
        )

    if not isinstance(config['default_path'], str) or not config['default_path'].strip():
        raise ValueError("'default_path' must be a non-empty string")

    chunk_size = config['default_chunk_size']

    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("'default_chunk_size' must be a positive integer")

    connection = config['connection']

    if not isinstance(connection, dict):
        raise ValueError("'connection' must be a dictionary")

    required_connection_keys = {'host', 'port'}
    missing_connection_keys = required_connection_keys - connection.keys()

    if missing_connection_keys:
        raise ValueError(
            f"Connection configuration is missing fields: {', '.join(sorted(missing_connection_keys))}"
        )

    host = connection['host']

    if not isinstance(host, str) or not host.strip():
        raise ValueError("'connection.host' must be a non-empty string")

    port = connection['port']

    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("'connection.port' must be an integer between 1 and 65535")
    

def get_config(default_config_path=DEFAULT_CONFIG_PATH) -> dict:
    config_path = pathlib.Path(default_config_path)

    if not config_path.exists():
        create_default_config(config_path)
        raise SystemExit(1)

    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    if config is None:
        raise ValueError("Config file is empty or invalid YAML format")

    if not isinstance(config, dict):
        raise ValueError("Config file must contain a dictionary at the top level")

    validate_config(config)

    return config