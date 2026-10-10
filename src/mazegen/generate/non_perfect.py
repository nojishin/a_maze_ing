import random

from visualizer.renderder import render_maze
from .maze_utils import MOVES, E, N, S, W, add_wall, remove_wall

DEAD_END_WALLS = 3


def is_dead_end(
    grid: list[list[int]],
    x: int,
    y: int,
    blocked: set[tuple[int, int]],
) -> bool:
    return (x, y) not in blocked and grid[y][x].bit_count() == DEAD_END_WALLS


def is_open_2x2(grid: list[list[int]], tx: int, ty: int) -> bool:
    if tx < 0 or ty < 0 or tx + 1 >= len(grid[0]) or ty + 1 >= len(grid):
        return False
    walls = (
        grid[ty][tx] & E
        | grid[ty + 1][tx] & E
        | grid[ty][tx] & S
        | grid[ty][tx + 1] & S
    )
    return walls == 0


def makes_open_2x2(
    grid: list[list[int]],
    x: int,
    y: int,
    direction: int,
) -> bool:
    if direction in (W, N):
        dx, dy, direction = MOVES[direction]
        x, y = x + dx, y + dy
    if direction == E:
        return is_open_2x2(grid, x, y - 1) or is_open_2x2(grid, x, y)
    return is_open_2x2(grid, x - 1, y) or is_open_2x2(grid, x, y)


def breakable_dirs(
    grid: list[list[int]],
    x: int,
    y: int,
    blocked: set[tuple[int, int]],
) -> list[int]:
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
        if not makes_open_2x2(grid, x, y, direction):
            dirs.append(direction)
        add_wall(grid, x, y, direction)
    return dirs


def add_loops(grid: list[list[int]], blocked: set[tuple[int, int]]) -> None:
    dead_ends = [
        (x, y)
        for y in range(len(grid))
        for x in range(len(grid[0]))
        if is_dead_end(grid, x, y, blocked)
    ]
    random.shuffle(dead_ends)
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
        remove_wall(grid, x, y, random.choice(best or dirs))
