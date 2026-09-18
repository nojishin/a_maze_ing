from .cli import get_config_path
from a_maze_ing.errors.exceptions import ConfigFileNotFoundError, ConfigFileReadError


def _read_config_file() -> str:
    file_path = get_config_path()
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError as e:
        raise ConfigFileNotFoundError(file_path) from e
    except (OSError, ValueError) as e:
        raise ConfigFileReadError(file_path, str(e)) from e

def parse_config():
