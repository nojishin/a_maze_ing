from errors.exceptions import MazeError
from errors.handler import error_handler
from input.maze_config import parse_config
from mazegen import MazeGenerator, MazegenError


def main() -> None:
    try:
        config = parse_config()
    except MazeError as e:
        error_handler(e)

    try:
        maze_generator = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            is_perfect=config.is_perfect,
            seed=config.seed,
        )
    except MazegenError as e:
        error_handler(e)
    maze_generator.generate()


if __name__ == "__main__":
    main()
