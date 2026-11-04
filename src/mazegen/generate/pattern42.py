from .maze_utils import MOVES, add_wall

PATTERN = [
    "X...XXX",
    "X.....X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX",
]


def make_blocked(width: int, height: int) -> set[tuple[int, int]]:
    """Compute the cells of the 42 pattern, centered in the maze.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        The ``(x, y)`` cells of the pattern, or an empty set if the maze is
        smaller than 9x7 and cannot display it.

    """
    if width < 9 or height < 7:
        return set()
    offset_x = (width - 7) // 2
    offset_y = (height - 5) // 2
    blocked: set[tuple[int, int]] = set()
    for j, line in enumerate(PATTERN):
        for i, char in enumerate(line):
            if char == "X":
                blocked.add((offset_x + i, offset_y + j))
    return blocked


def close_blocked(
    grid: list[list[int]], blocked: set[tuple[int, int]],
) -> None:
    """Close all four walls of every cell of the 42 pattern.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        blocked: Cells reserved for the 42 pattern.

    """
    for x, y in blocked:
        for direction in MOVES:
            add_wall(grid, x, y, direction)
