from pathlib import Path

from pydantic import ValidationError

from a_maze_ing.errors.exceptions import (
    ConfigDuplicateKeyError,
    ConfigFileFormatError,
    ConfigFileNotFoundError,
    ConfigFileReadError,
    ConfigValidationError,
)
from a_maze_ing.models.config import Config

from .cli import get_config_path


def _read_config_file(path: Path) -> str:
    try:
        with Path.open(path) as f:
            return f.read()
    except FileNotFoundError as e:
        raise ConfigFileNotFoundError(path) from e
    except (OSError, ValueError) as e:
        raise ConfigFileReadError(path, str(e)) from e


def _extract_dict(text: str) -> dict[str, str]:
    text_splitlines = text.splitlines()
    result: dict[str, str] = {}
    for i, line in enumerate(text_splitlines):
        if line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise ConfigFileFormatError(line)
        if key in result:
            raise ConfigDuplicateKeyError(key, i + 1)
        result[key] = value
    return result


def _validate_config(config_dict: dict[str, str]) -> Config:
    try:
        config = Config.model_validate(config_dict)
    except ValidationError as e:
        raise ConfigValidationError(str(e)) from e
    return config


def parse_config() -> Config:
    config_path = get_config_path()
    config_text = _read_config_file(config_path)
    config_dict = _extract_dict(config_text)
    return _validate_config(config_dict)
