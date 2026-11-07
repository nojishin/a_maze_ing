import sys
from pathlib import Path

from errors.exceptions import MazeError, OutputFileWriteError
from errors.handler import error_handler
from input.maze_config import parse_config
from mazegen import MazeGenerator, MazeGenError
from visualizer.renderder import render_maze


def print_maze(
    *,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],  # noqa: A002 - pairs with `entry`
    path: list[tuple[int, int]],
    show_path: bool,
) -> None:
    """Print the maze to the terminal.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        entry: The ``(x, y)`` entry cell.
        exit: The ``(x, y)`` exit cell.
        path: Cells of the solution path, from entry to exit.
        show_path: Whether to draw the solution path.

    """
    if show_path:
        print(render_maze(grid, entry, exit, path))
    else:
        print(render_maze(grid, entry, exit))


def write_file(
    *,
    output_file: Path,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],  # noqa: A002 - pairs with `entry`
    directions: str,
) -> None:
    """Write the maze, entry, exit and solution to the output file.

    The grid is written one row per line, with each cell as a hex digit,
    followed by an empty line, the entry, the exit and the path directions.

    Args:
        output_file: Path of the file to write.
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        entry: The ``(x, y)`` entry cell.
        exit: The ``(x, y)`` exit cell.
        directions: The solution path as a string of ``N``, ``E``, ``S``
            and ``W``.

    Raises:
        OutputFileWriteError: If the file cannot be written.

    """
    texts: list[str] = [
        *("".join(f"{v:x}" for v in row) for row in grid),
        "",
        ", ".join(map(str, entry)),
        ", ".join(map(str, exit)),
        directions,
    ]
    text = "\n".join(texts)
    try:
        with Path.open(output_file, mode="w") as f:
            f.write(text)
    except (OSError, ValueError) as e:
        raise OutputFileWriteError(output_file, str(e)) from e


def main() -> None:
    """Read the config, then run the interactive command loop.

    Errors are printed and the program exits with status 1.

    """
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
    except MazeGenError as e:
        error_handler(e)

    print(
        "=== A-Maze-ing ===\n"
        "Commands:\n"
        "generate (g) : generate a new maze\n"
        "path     (p) : show / hide the solution path\n"
        "exit     (q) : quit\n",
    )
    show_path = True
    try:
        while True:
            try:
                cmd = input("> ").strip().lower()
            except EOFError:
                print()
                sys.exit(0)
            match cmd:
                case "generate" | "g":
                    grid = maze_generator.generate()
                    path = maze_generator.solve()
                    print_maze(
                        grid=grid,
                        entry=config.entry,
                        exit=config.exit,
                        path=path.coord,
                        show_path=show_path,
                    )
                    write_file(
                        output_file=config.output_file,
                        grid=grid,
                        entry=config.entry,
                        exit=config.exit,
                        directions=path.directions,
                    )
                case "path" | "p":
                    if show_path:
                        show_path = False
                        print("Solution path: hidden")
                    else:
                        show_path = True
                        print("Solution path: shown")
                case "exit" | "q":
                    break
                case _:
                    print(f"Unknown command: '{cmd}'")
    except (MazeError, MazeGenError) as e:
        error_handler(e)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)
    except Exception as e:  # noqa: BLE001 - for subject
        print(str(e))
        sys.exit(1)
