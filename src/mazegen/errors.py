from pydantic import ValidationError
from pydantic_core import ErrorDetails


class MazeGenError(Exception):
    """Base class for errors raised by the mazegen package."""


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


class ParamsValidationError(MazeGenError):
    """Raised when maze parameters fail validation."""

    def __init__(self, validation_error: ValidationError) -> None:
        """Build a message listing every invalid value.

        Args:
            validation_error: The error raised by pydantic.

        """
        lines = ["Invalid parameter values:"]
        lines.extend(
            _format_error(error) for error in validation_error.errors()
        )
        super().__init__("\n".join(lines))


class PathNotFoundError(MazeGenError):
    """Raised when no path connects the entry and the exit."""

    def __init__(self) -> None:
        """Build the error message."""
        super().__init__("Path not found")


class MazeNotGeneratedError(MazeGenError):
    """Raised when the maze is solved before it is generated."""

    def __init__(self) -> None:
        """Build the error message."""
        super().__init__("Maze not generated. Call generate() first.")
