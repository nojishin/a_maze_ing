import sys
from pathlib import Path

from errors.exceptions import MazeError, OutputFileWriteError
from errors.handler import error_handler
from input.maze_config import parse_config
from mazegen import MazeGenerator, MazeGenError
from visualizer.renderder import render_maze

WALL_COLORS = [
    "\033[47m  \033[0m",
    "\033[44m  \033[0m",
    "\033[43m  \033[0m",
    "\033[45m  \033[0m",
]

HELP_MSG = (
    "=== A-Maze-ing ===\n"
    "Commands:\n"
    "generate (g) : generate a new maze\n"
    "path     (p) : show / hide the solution path\n"
    "color    (c) : change wall color\n"
    "help     (h) : show this message\n"
    "exit     (q) : quit\n"
)


def print_maze(  # noqa: PLR0913 - keyword-only, one arg per maze part
    *,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],  # noqa: A002 - pairs with `entry`
    path: list[tuple[int, int]],
    wall: str,
    show_path: bool,
) -> None:
    """Print the maze to the terminal.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        entry: The ``(x, y)`` entry cell.
        exit: The ``(x, y)`` exit cell.
        path: Cells of the solution path, from entry to exit.
        wall: The colored block used to draw walls.
        show_path: Whether to draw the solution path.

    """
    if show_path:
        print(render_maze(grid, entry, exit, wall, path))
    else:
        print(render_maze(grid, entry, exit, wall))


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
        "",
    ]
    text = "\n".join(texts)
    try:
        with Path.open(output_file, mode="w") as f:
            f.write(text)
    except (OSError, ValueError) as e:
        raise OutputFileWriteError(output_file, str(e)) from e


def main() -> None:  # noqa: C901 - flat command dispatch in one match
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

    print(HELP_MSG)
    show_path = True
    color_idx = 0
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
                    if not maze_generator.has_42pattern():
                        print(
                            "Warning: the 42 pattern could not be embedded ",
                            "(maze too small).",
                        )
                    print_maze(
                        grid=grid,
                        entry=config.entry,
                        exit=config.exit,
                        path=path.coord,
                        wall=WALL_COLORS[color_idx],
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
                    print_maze(
                        grid=grid,
                        entry=config.entry,
                        exit=config.exit,
                        path=path.coord,
                        wall=WALL_COLORS[color_idx],
                        show_path=show_path,
                    )
                case "color" | "c":
                    color_idx = (color_idx + 1) % len(WALL_COLORS)
                    print_maze(
                        grid=grid,
                        entry=config.entry,
                        exit=config.exit,
                        path=path.coord,
                        wall=WALL_COLORS[color_idx],
                        show_path=show_path,
                    )
                case "help" | "h":
                    print(HELP_MSG)
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
