import random
from collections import deque

from mazegen.errors import PatternOverlapError
from mazegen.models import MazeParams
from visualizer.diff_renderer import debug_printer

from .maze_utils import MOVES, E, N, S, W, add_wall, remove_wall
from .non_perfect import add_loops
from .pattern42 import close_blocked, make_blocked

MIN_DIVIDE_SIZE = 2


def choose_orientation(width: int, height: int, rnd: random.Random) -> bool:
    """Choose the orientation of the next dividing wall.

    The wall is placed across the longer side of the area. If the area is
    square, the orientation is chosen at random.

    Args:
        width: Width of the area in cells.
        height: Height of the area in cells.
        rnd: Random number generator used for the choice.

    Returns:
        True for a horizontal wall, False for a vertical wall.

    """
    if width < height:
        return True
    if width > height:
        return False
    return rnd.choice([True, False])


def init_grid(width: int, height: int) -> list[list[int]]:
    """Create a grid whose only walls are the outer border.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        A grid of wall bitmasks, indexed as ``grid[y][x]``.

    """
    grid = [[0] * width for _ in range(height)]
    for x in range(width):
        grid[0][x] |= N
        grid[height - 1][x] |= S
    for y in range(height):
        grid[y][0] |= W
        grid[y][width - 1] |= E
    return grid


def flood(
    grid: list[list[int]],
    start: tuple[int, int],
    visited: set[tuple[int, int]],
) -> None:
    """Mark every cell reachable from a start cell, using BFS.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        start: The ``(x, y)`` cell to start from.
        visited: Set of reached cells, updated in place. Cells already in it
            are not explored again.

    """
    queue = deque([start])
    visited.add(start)
    while queue:
        x, y = queue.popleft()
        for direction, (dx, dy, _) in MOVES.items():
            if grid[y][x] & direction:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            visited.add((nx, ny))
            queue.append((nx, ny))


def find_candidates(
    grid: list[list[int]],
    visited: set[tuple[int, int]],
    blocked: set[tuple[int, int]],
) -> list[tuple[int, int, int]]:
    """Find the walls that separate reached cells from unreached ones.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        visited: Cells already reached.
        blocked: Cells reserved for the 42 pattern.

    Returns:
        An ``(x, y, direction)`` tuple for each wall between a visited cell and
        an unvisited, unblocked cell inside the maze.

    """
    height = len(grid)
    width = len(grid[0])
    candidates = []
    for x, y in visited:
        for direction, (dx, dy, _) in MOVES.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in visited or (nx, ny) in blocked:
                continue
            candidates.append((x, y, direction))
    return candidates


def repair(
    grid: list[list[int]],
    blocked: set[tuple[int, int]],
    rnd: random.Random,
) -> None:
    """Reconnect all cells outside the 42 pattern, in place.

    Starting from ``(0, 0)``, a random wall on the edge of the reached region
    is removed until no unreached cell remains.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        blocked: Cells reserved for the 42 pattern.
        rnd: Random number generator used to pick walls.

    """
    visited: set[tuple[int, int]] = set()
    flood(grid, (0, 0), visited)
    while True:
        candidates = find_candidates(grid, visited, blocked)
        if not candidates:
            return
        x, y, direction = rnd.choice(candidates)
        remove_wall(grid, x, y, direction)
        dx, dy, _ = MOVES[direction]
        flood(grid, (x + dx, y + dy), visited)


def divide_horizontal(  # noqa: PLR0913, PLR0917 - recursive area split
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
    rnd: random.Random,
) -> None:
    """Split an area with a horizontal wall, then divide both parts.

    The wall has one random passage in it.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        x: Column of the left edge of the area.
        y: Row of the top edge of the area.
        width: Width of the area in cells.
        height: Height of the area in cells.
        rnd: Random number generator for walls and passages.

    """
    wall_y = y + rnd.randint(0, height - 2)
    passage_x = rnd.randint(x, x + width - 1)
    for col in range(x, x + width):
        if col == passage_x:
            continue
        add_wall(grid, col, wall_y, S)
    divide(grid, x, y, width, wall_y - y + 1, rnd)
    divide(grid, x, wall_y + 1, width, y + height - wall_y - 1, rnd)


def divide_vertical(  # noqa: PLR0913, PLR0917 - recursive area split
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
    rnd: random.Random,
) -> None:
    """Split an area with a vertical wall, then divide both parts.

    The wall has one random passage in it.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        x: Column of the left edge of the area.
        y: Row of the top edge of the area.
        width: Width of the area in cells.
        height: Height of the area in cells.
        rnd: Random number generator for walls and passages.

    """
    wall_x = x + rnd.randint(0, width - 2)
    passage_y = rnd.randint(y, y + height - 1)
    for row in range(y, y + height):
        if row == passage_y:
            continue
        add_wall(grid, wall_x, row, E)
    divide(grid, x, y, wall_x - x + 1, height, rnd)
    divide(grid, wall_x + 1, y, x + width - wall_x - 1, height, rnd)


def divide(  # noqa: PLR0913, PLR0917 - recursive area split
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
    rnd: random.Random,
) -> None:
    """Divide an area recursively until it is too small to split.

    Recursion stops when the width or height of the area is less than 2.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        x: Column of the left edge of the area.
        y: Row of the top edge of the area.
        width: Width of the area in cells.
        height: Height of the area in cells.
        rnd: Random number generator for walls and passages.

    """
    if width < MIN_DIVIDE_SIZE or height < MIN_DIVIDE_SIZE:
        return
    is_horizontal = choose_orientation(width, height, rnd)
    if is_horizontal:
        divide_horizontal(grid, x, y, width, height, rnd)
        debug_printer.show(grid, "divide_horizonal")
    else:
        divide_vertical(grid, x, y, width, height, rnd)
        debug_printer.show(grid, "divide_vertical")


def generate(maze_params: MazeParams, rnd: random.Random) -> list[list[int]]:
    """Generate a maze containing the 42 pattern.

    The maze is built by recursive division. The 42 pattern is then closed off
    and the remaining cells are reconnected. Loops are added if the maze is not
    perfect.

    Args:
        maze_params: Size, entry, exit and perfection settings of the maze.
        rnd: Random number generator for walls, passages and loops. Its
            state advances, so reusing it gives a different maze each call.

    Returns:
        A grid of wall bitmasks, indexed as ``grid[y][x]``.

    Raises:
        MazeError: If the maze is too small to display the 42 pattern, or if
            the entry or exit overlaps it.

    """
    width = maze_params.width
    height = maze_params.height
    grid = init_grid(width, height)
    blocked = make_blocked(width, height)
    if maze_params.entry in blocked or maze_params.exit in blocked:
        raise PatternOverlapError
    debug_printer.reset(maze_params.entry, maze_params.exit)
    debug_printer.show(grid, "init")
    divide(grid, 0, 0, width, height, rnd)
    debug_printer.show(grid, "divide")
    close_blocked(grid, blocked)
    debug_printer.show(grid, "close_blocked")
    repair(grid, blocked, rnd)
    debug_printer.show(grid, "repair")
    if not maze_params.is_perfect:
        add_loops(grid, blocked, rnd)
        debug_printer.show(grid, "add_loops")
    return grid
