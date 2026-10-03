from pathlib import Path

from pydantic import ValidationError
from pydantic_core import ErrorDetails


class MazeError(Exception): ...


class InvalidArgumentsCountError(MazeError):
    def __init__(self, count: int) -> None:
        super().__init__(
            "Usage: python3 a_maze_ing.py <config_file>\n"
            f"Expected 1 argument, but got {count}",
        )


class ConfigFileNotFoundError(MazeError):
    def __init__(self, file_path: Path) -> None:
        super().__init__(f"Config File not found: {file_path!r}")


class ConfigFileReadError(MazeError):
    def __init__(self, file_path: Path, reason: str) -> None:
        super().__init__(f"Failed to read config file {file_path!r}: {reason}")


class ConfigFileFormatError(MazeError):
    def __init__(self, line: str) -> None:
        super().__init__(f"Invalid config file format {line!r}")


class ConfigDuplicateKeyError(MazeError):
    def __init__(self, key: str, line_no: int) -> None:
        super().__init__(f"Duplicate key {key!r} found at line {line_no}")


def _format_error(error: ErrorDetails) -> str:

    message = ""
    key = error["loc"]
    reason = error["msg"]
    input_value = error["input"]
    if key:
        message += ".".join(map(str, key))
        message += ": "
    message += reason
    if key and error["type"] != "missing":
        message += f" (got {input_value!r})"
    return message


class ConfigValidationError(MazeError):
    def __init__(self, validation_error: ValidationError) -> None:
        lines = ["Invalid config values:"]
        lines.extend(_format_error(error) for error in validation_error.errors())
        super().__init__("\n".join(lines))
