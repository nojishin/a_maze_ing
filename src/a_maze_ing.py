import sys

from errors.exceptions import MazeError
from errors.handler import error_handler
from input.maze_config import parse_config
from mazegen import MazeGenerator, MazegenError
from visualizer.renderder import render_maze


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

    print(
        "=== A-Maze-ing ===\n"
        "Commands:\n"
        "generate (g) : generate a new maze\n"
        "route    (r) : show / hide the solution path\n"
        "exit     (e) : quit\n",
    )
    while True:
        try:
            cmd = input("> ").strip().lower()
        except EOFError:
            print()
            sys.exit(0)
        match cmd:
            case "generate" | "g":
                print("generate called from main")
                result = maze_generator.generate()
                render_maze(result)
            case "route" | "r":
                print("route called from main")
            case "exit" | "e":
                break
            case _:
                print(f"Unknown command: '{cmd}'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)
