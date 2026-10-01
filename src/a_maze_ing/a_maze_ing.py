from a_maze_ing.input.maze_config import parse_config
from a_maze_ing.errors.exceptions import MazeError
from a_maze_ing.errors.handler import error_handler


def main() -> None:
    try:
        config = parse_config()
    except MazeError as e:
        error_handler(e)


if __name__ == "__main__":
    main()
