import yaml
import pathlib

DEFAULT_CONFIG_PATH = pathlib.Path(__file__).parents[3] / 'config/config.yaml'
DEFAULT_CONFIG_KEYS = {'default_path', 'connection'}

def get_config(default_config_path=DEFAULT_CONFIG_PATH) -> dict:
    config_path = default_config_path

    # check if the config file exists
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    if config is None:
        raise ValueError("Config file is empty or invalid YAML format")

    if not isinstance(config, dict):
        raise ValueError("Config file must contain a dictionary at the top level")

    # validate that required fields are present
    is_default_path_not_set = not config.get('default_path')
    is_connection_not_set = not config.get('connection')

    if is_default_path_not_set or is_connection_not_set:
        raise ValueError("Config file is missing required fields: 'default_path' and/or 'connection'")

    default_path_exists = pathlib.Path(config['default_path']).exists()

    # validate that the default path exists
    if not default_path_exists:
        raise ValueError(f"Default path does not exist: {config['default_path']}")
    
    return config