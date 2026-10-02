from errors.exceptions import MazeError
from errors.handler import error_handler
from input.maze_config import parse_config


def main() -> None:
    try:
        config = parse_config()
    except MazeError as e:
        error_handler(e)


if __name__ == "__main__":
    main()
