from .maze_utils import MOVES, add_wall

PATTERN = [
    "X...XXX",
    "X.....X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX",
]

PATTERN_WIDTH = len(PATTERN[0])
PATTERN_HEIGHT = len(PATTERN)
PATTERN_MARGIN = 1
MIN_WIDTH = PATTERN_WIDTH + 2 * PATTERN_MARGIN
MIN_HEIGHT = PATTERN_HEIGHT + 2 * PATTERN_MARGIN


def make_blocked(width: int, height: int) -> set[tuple[int, int]]:
    """Compute the cells of the 42 pattern, centered in the maze.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        The ``(x, y)`` cells of the pattern, or an empty set if the maze is
        smaller than 9x7 and cannot display it.

    """
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return set()
    offset_x = (width - PATTERN_WIDTH) // 2
    offset_y = (height - PATTERN_HEIGHT) // 2
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
