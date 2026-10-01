import sys

from a_maze_ing.errors.exceptions import MazeError


def error_handler(error: MazeError) -> None:
    print(str(error))
    sys.exit(1)
