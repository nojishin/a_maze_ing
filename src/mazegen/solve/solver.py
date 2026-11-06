from collections import deque
from itertools import pairwise

from mazegen.errors import PathNotFoundError
from mazegen.models import PathResult

N = 0b0001
E = 0b0010
S = 0b0100
W = 0b1000

DIRS = {N: (0, -1), E: (1, 0), S: (0, 1), W: (-1, 0)}
DELTA_TO_DIR = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}

Coord = tuple[int, int]




def solve(
    grid: list[list[int]],
    start: Coord,
    goal: Coord,
) -> PathResult:
    """Find the shortest path between two cells, using BFS.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        start: The ``(x, y)`` start cell.
        goal: The ``(x, y)`` goal cell.

    Returns:
        The path cells and directions.

    Raises:
        PathNotFoundError: If the goal cannot be reached.

    """
    h, w = len(grid), len(grid[0])
    prev: list[list[Coord | None]] = [[None] * w for _ in range(h)]
    sx, sy = start
    gx, gy = goal
    prev[sy][sx] = start
    que = deque([start])

    while que:
        x, y = que.popleft()
        if (x, y) == goal:
            break

        for d, (dx, dy) in DIRS.items():
            if d & grid[y][x]:
                continue
            nx, ny = x + dx, y + dy
            if not (0 <= ny < h and 0 <= nx < w):
                continue
            if prev[ny][nx] is not None:
                continue
            prev[ny][nx] = (x, y)
            que.append((nx, ny))
    if prev[gy][gx] is None:
        raise PathNotFoundError

    path = [goal]
    while path[-1] != start:
        x, y = path[-1]
        p = prev[y][x]
        if p is None:
            raise PathNotFoundError
        path.append(p)
    path.reverse()

    direction = "".join(
        DELTA_TO_DIR[(b[0] - a[0], b[1] - a[1])] for a, b in pairwise(path)
    )

    return PathResult(coord=path, directions=direction)
