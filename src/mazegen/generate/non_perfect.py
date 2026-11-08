import random

from .maze_utils import MOVES, E, N, S, W, add_wall, remove_wall

DEAD_END_WALLS = 3
OPEN_AREA_SIZE = 3


def is_dead_end(
    grid: list[list[int]],
    x: int,
    y: int,
    blocked: set[tuple[int, int]],
) -> bool:
    """Check whether a cell is a dead end outside the 42 pattern.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        x: Column of the cell.
        y: Row of the cell.
        blocked: Cells reserved for the 42 pattern.

    Returns:
        True if the cell is not blocked and has exactly three walls.

    """
    return (x, y) not in blocked and grid[y][x].bit_count() == DEAD_END_WALLS


def is_open_area(grid: list[list[int]], tx: int, ty: int) -> bool:
    """Check whether a 3x3 area has no walls inside it.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        tx: Column of the top-left cell of the area.
        ty: Row of the top-left cell of the area.

    Returns:
        True if the area fits in the maze and all its inner walls are open.

    """
    size = OPEN_AREA_SIZE
    if tx < 0 or ty < 0 or tx + size > len(grid[0]) or ty + size > len(grid):
        return False
    for y in range(ty, ty + size):
        for x in range(tx, tx + size):
            if x < tx + size - 1 and grid[y][x] & E:
                return False
            if y < ty + size - 1 and grid[y][x] & S:
                return False
    return True


def makes_open_area(
    grid: list[list[int]],
    x: int,
    y: int,
    direction: int,
) -> bool:
    """Check whether an opened edge belongs to an open 3x3 area.

    The wall must already be removed from the grid. ``N`` and ``W`` edges are
    converted to the matching ``S`` and ``E`` edges of the neighboring cell,
    then the six 3x3 areas containing the edge are checked.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        x: Column of the cell.
        y: Row of the cell.
        direction: Side of the cell that was opened.

    Returns:
        True if any 3x3 area containing the edge is fully open.

    """
    if direction in (W, N):
        dx, dy, direction = MOVES[direction]
        x, y = x + dx, y + dy
    size = OPEN_AREA_SIZE
    if direction == E:
        xs = range(x - size + 2, x + 1)
        ys = range(y - size + 1, y + 1)
    else:
        xs = range(x - size + 1, x + 1)
        ys = range(y - size + 2, y + 1)
    return any(is_open_area(grid, tx, ty) for ty in ys for tx in xs)


def breakable_dirs(
    grid: list[list[int]],
    x: int,
    y: int,
    blocked: set[tuple[int, int]],
) -> list[int]:
    """List the walls of a cell that can safely be removed.

    A wall is breakable if it is closed, is not on the maze border, does not
    lead to a blocked cell, and does not create an open 3x3 area when removed.
    Each wall is removed temporarily to test it, then restored.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        x: Column of the cell.
        y: Row of the cell.
        blocked: Cells reserved for the 42 pattern.

    Returns:
        The directions of the breakable walls.

    """
    width = len(grid[0])
    height = len(grid)
    dirs = []
    for direction, (dx, dy, _) in MOVES.items():
        nx, ny = x + dx, y + dy
        if not grid[y][x] & direction:
            continue
        if not (0 <= nx < width and 0 <= ny < height):
            continue
        if (nx, ny) in blocked:
            continue
        remove_wall(grid, x, y, direction)
        if not makes_open_area(grid, x, y, direction):
            dirs.append(direction)
        add_wall(grid, x, y, direction)
    return dirs


def add_loops(
    grid: list[list[int]],
    blocked: set[tuple[int, int]],
    rnd: random.Random,
) -> None:
    """Create loops by opening a wall of each dead end, in place.

    Dead ends are visited in random order. A wall shared with another dead end
    is preferred, so one removal can clear both. Dead ends with no breakable
    wall are left unchanged.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        blocked: Cells reserved for the 42 pattern.
        rnd: Random number generator for the order and wall choice.

    """
    dead_ends = [
        (x, y)
        for y in range(len(grid))
        for x in range(len(grid[0]))
        if is_dead_end(grid, x, y, blocked)
    ]
    rnd.shuffle(dead_ends)
    for x, y in dead_ends:
        if not is_dead_end(grid, x, y, blocked):
            continue
        dirs = breakable_dirs(grid, x, y, blocked)
        if not dirs:
            continue
        best = [
            d for d in dirs
            if is_dead_end(grid, x + MOVES[d][0], y + MOVES[d][1], blocked)
        ]
        remove_wall(grid, x, y, rnd.choice(best or dirs))
