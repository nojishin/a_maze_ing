"""Helpers that check a generated maze independently of mazegen."""

import random
from collections import deque
from dataclasses import dataclass

from mazegen import PathResult
from mazegen.generate.pattern42 import make_blocked

N, E, S, W = 1, 2, 4, 8
ALL_WALLS = N | E | S | W
MOVES = {N: (0, -1, S), E: (1, 0, W), S: (0, 1, N), W: (-1, 0, E)}
LETTER = {"N": N, "E": E, "S": S, "W": W}
MIN_SIZE = 3
MAX_SIZE = 100
OPEN_AREA = 3

Coord = tuple[int, int]
Grid = list[list[int]]


@dataclass
class Params:
    """Arguments passed to MazeGenerator."""

    width: int
    height: int
    entry: Coord
    exit: Coord
    is_perfect: bool
    seed: int


def random_params(*, perfect: bool | None = None) -> Params:
    """Pick random valid params (entry/exit outside the 42 pattern)."""
    if perfect is None:
        perfect = random.choice([True, False])
    width = random.randint(MIN_SIZE, MAX_SIZE)
    height = random.randint(MIN_SIZE, MAX_SIZE)
    blocked = make_blocked(width, height)
    free = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in blocked
    ]
    entry, exit_ = random.sample(free, 2)
    return Params(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        is_perfect=perfect,
        seed=random.randrange(2**32),
    )


def bfs(grid: Grid, start: Coord) -> dict[Coord, int]:
    """Return the distance from start to every reachable cell."""
    h, w = len(grid), len(grid[0])
    dist = {start: 0}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for d, (dx, dy, _) in MOVES.items():
            nx, ny = x + dx, y + dy
            if grid[y][x] & d or not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) not in dist:
                dist[(nx, ny)] = dist[(x, y)] + 1
                queue.append((nx, ny))
    return dist


def wall_errors(grid: Grid) -> list[str]:
    """Check border walls and neighbour coherence."""
    errors = []
    h, w = len(grid), len(grid[0])
    for y in range(h):
        for x in range(w):
            for d, (dx, dy, opp) in MOVES.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    if not grid[y][x] & d:
                        errors.append(f"open border at {(x, y)} dir={d}")
                elif bool(grid[y][x] & d) != bool(grid[ny][nx] & opp):
                    errors.append(f"incoherent wall {(x, y)}-{(nx, ny)}")
    return errors


def count_open_edges(grid: Grid) -> int:
    """Count open inner edges (each counted once via E and S)."""
    h, w = len(grid), len(grid[0])
    count = 0
    for y in range(h):
        for x in range(w):
            if x + 1 < w and not grid[y][x] & E:
                count += 1
            if y + 1 < h and not grid[y][x] & S:
                count += 1
    return count


def find_open_area(grid: Grid) -> Coord | None:
    """Return the top-left of a 3x3 area with no inner walls, if any."""
    h, w = len(grid), len(grid[0])
    for ty in range(h - OPEN_AREA + 1):
        for tx in range(w - OPEN_AREA + 1):
            if all(
                not (x < tx + OPEN_AREA - 1 and grid[y][x] & E)
                and not (y < ty + OPEN_AREA - 1 and grid[y][x] & S)
                for y in range(ty, ty + OPEN_AREA)
                for x in range(tx, tx + OPEN_AREA)
            ):
                return (tx, ty)
    return None


def path_errors(
    grid: Grid,
    p: Params,
    path: PathResult,
    dist: dict[Coord, int],
) -> list[str]:
    """Check that the solution is a valid shortest path."""
    coord, directions = path.coord, path.directions
    if not coord or coord[0] != p.entry or coord[-1] != p.exit:
        return ["path does not go from entry to exit"]
    if len(directions) != len(coord) - 1:
        return ["directions length != coord length - 1"]
    x, y = p.entry
    for ch, nxt in zip(directions, coord[1:], strict=True):
        d = LETTER.get(ch)
        if d is None or grid[y][x] & d:
            return [f"path goes through a wall at {(x, y)} '{ch}'"]
        dx, dy, _ = MOVES[d]
        x, y = x + dx, y + dy
        if (x, y) != nxt:
            return [f"directions and coord disagree at {nxt}"]
    if len(directions) != dist.get(p.exit):
        return [f"path not shortest: {len(directions)} vs {dist.get(p.exit)}"]
    return []


def maze_errors(grid: Grid, p: Params, path: PathResult) -> list[str]:
    """Run every check on a generated maze and its solution.

    Returns:
        A message for each problem found; empty if the maze is valid.

    """
    if len(grid) != p.height or any(len(r) != p.width for r in grid):
        return ["grid size mismatch"]

    errors = wall_errors(grid)
    blocked = make_blocked(p.width, p.height)
    errors.extend(
        f"pattern cell {c} not closed"
        for c in blocked
        if grid[c[1]][c[0]] != ALL_WALLS
    )

    dist = bfs(grid, p.entry)
    cells = p.width * p.height - len(blocked)
    if len(dist) != cells:
        errors.append(f"unreachable cells: {cells - len(dist)}")
    if p.is_perfect and count_open_edges(grid) != cells - 1:
        errors.append("perfect maze has loops")
    open_area = find_open_area(grid)
    if open_area is not None:
        errors.append(f"3x3 open area at {open_area}")

    errors.extend(path_errors(grid, p, path, dist))
    return errors
