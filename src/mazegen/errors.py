from pydantic import ValidationError
from pydantic_core import ErrorDetails


class MazegenError(Exception): ...


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


class ParamsValidationError(MazegenError):
    def __init__(self, validation_error: ValidationError) -> None:
        lines = ["Invalid parameter values:"]
        lines.extend(
            _format_error(error) for error in validation_error.errors()
        )
        super().__init__("\n".join(lines))
