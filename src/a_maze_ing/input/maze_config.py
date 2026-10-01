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
    # remove comments
    text_splitlines = [line for line in text_splitlines if not line.startswith("#")]
    print("remove:", text_splitlines)
    result: dict[str, str] = {}
    for i, line in enumerate(text_splitlines):
        split_str = line.split("=", 1)
        print(f"{line}({len(split_str)}), ", end="")
        if len(split_str) != 2:
            raise ConfigFileFormatError(line)
        if split_str[0] in result:
            raise ConfigDuplicateKeyError(split_str[0], i + 1)
        result[split_str[0]] = split_str[1]
    print("\n\nresult:", result)
    return result



# ! test
def main() -> None:
    text = _read_config_file(get_config_path())
    d = _extract_dict(text)
    print(d)


main()
