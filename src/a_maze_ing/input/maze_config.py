from .cli import get_config_path
from pathlib import Path

from a_maze_ing.errors.exceptions import (
    ConfigFileNotFoundError,
    ConfigFileReadError,
    ConfigFileFormatError,
    ConfigDuplicateKeyError,
)


def _read_config_file(path: Path) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError as e:
        raise ConfigFileNotFoundError(path) from e
    except (OSError, ValueError) as e:
        raise ConfigFileReadError(path, str(e)) from e


def _extract_dict(text: str) -> dict[str, str]:
    text_splitlines = text.splitlines()
    print("textsplitlines:", text_splitlines)
    result: dict[str, str] = {}
    for i, line in enumerate(text_splitlines):
        if line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise ConfigFileFormatError(line)
        print(f"{line}({sep}), ", end="")
        if key in result:
            raise ConfigDuplicateKeyError(key, i + 1)
        result[key] = value
    print("\n\nresult:", result)
    return result


# ! test
def main() -> None:
    text = _read_config_file(get_config_path())
    d = _extract_dict(text)
    print(d)


main()
