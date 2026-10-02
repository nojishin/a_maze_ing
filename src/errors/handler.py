import sys

from errors.exceptions import MazeError


def error_handler(error: MazeError) -> None:
    print(str(error))
    sys.exit(1)
