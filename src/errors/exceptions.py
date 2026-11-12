from pathlib import Path

from pydantic import ValidationError
from pydantic_core import ErrorDetails


class MazeError(Exception):
    """Base class for errors raised by the a_maze_ing program."""


class InvalidArgumentsCountError(MazeError):
    """Raised when the program gets the wrong number of arguments."""

    def __init__(self, count: int) -> None:
        """Build the usage message.

        Args:
            count: Number of items in ``sys.argv``.

        """
        super().__init__(
            "Usage: python3 a_maze_ing.py <config_file>\n"
            f"Expected 1 argument, but got {count}",
        )


class ConfigFileNotFoundError(MazeError):
    """Raised when the config file does not exist."""

    def __init__(self, file_path: Path) -> None:
        """Build the error message.

        Args:
            file_path: Path of the missing config file.

        """
        super().__init__(f"Config file not found: {file_path!r}")


class ConfigFileReadError(MazeError):
    """Raised when the config file cannot be read."""

    def __init__(self, file_path: Path, reason: str) -> None:
        """Build the error message.

        Args:
            file_path: Path of the config file.
            reason: Why reading failed.

        """
        super().__init__(f"Failed to read config file {file_path!r}: {reason}")


class ConfigFileFormatError(MazeError):
    """Raised when a config line is not in ``KEY=VALUE`` format."""

    def __init__(self, line: str) -> None:
        """Build the error message.

        Args:
            line: The invalid line.

        """
        super().__init__(f"Invalid config file format {line!r}")


class OutputFileWriteError(MazeError):
    """Raised when the output file cannot be written."""

    def __init__(self, file_path: Path, reason: str) -> None:
        """Build the error message.

        Args:
            file_path: Path of the output file.
            reason: Why writing failed.

        """
        super().__init__(
            f"Failed to write output file {file_path!r}: {reason}",
        )


class ConfigDuplicateKeyError(MazeError):
    """Raised when a key appears more than once in the config file."""

    def __init__(self, key: str, line_no: int) -> None:
        """Build the error message.

        Args:
            key: The duplicated key.
            line_no: Line number of the second occurrence, starting at 1.

        """
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
    """Raised when config values fail validation."""

    def __init__(self, validation_error: ValidationError) -> None:
        """Build a message listing every invalid value.

        Args:
            validation_error: The error raised by pydantic.

        """
        lines = ["Invalid config values:"]
        lines.extend(
            _format_error(error) for error in validation_error.errors()
        )
        super().__init__("\n".join(lines))


class OutputFileConflictError(MazeError):
    """Raised when the output file is the config file itself."""

    def __init__(self, path: Path) -> None:
        """Build the error message.

        Args:
            path: Path of the output file.

        """
        super().__init__(
            f"OUTPUT_FILE must not be the config file itself: '{path}'",
        )
