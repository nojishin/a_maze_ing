import random

from .maze_utils import MOVES, E, S, add_wall, remove_wall
from visualizer.renderder import render_maze


def wall_candidates(
    grid: list[list[int]],
    blocked: set[tuple[int, int]],
) -> list[tuple[int, int, int]]:
    width = len(grid[0])
    height = len(grid)
    candidates = []
    for y in range(height):
        for x in range(width):
            for direction in (E, S):
                dx, dy, _ = MOVES[direction]
                nx, ny = x + dx, y + dy
                if nx >= width or ny >= height:
                    continue
                if (x, y) in blocked or (nx, ny) in blocked:
                    continue
                if grid[y][x] & direction == 0:
                    continue
                candidates.append((x, y, direction))
    return candidates


def is_open3x3(grid: list[list[int]], tx: int, ty: int) -> bool:
    for y in range(ty, ty + 3):
        for x in range(tx, tx + 3):
            if x < tx + 2 and grid[y][x] & E:
                return False
            if y < ty + 2 and grid[y][x] & S:
                return False
    return True


def makes_open_area(grid: list[list[int]], x: int, y: int) -> bool:
    width = len(grid[0])
    height = len(grid)
    for ty in range(y - 2, y + 1):
        for tx in range(x - 2, x + 1):
            if tx < 0 or ty < 0 or tx + 2 >= width or ty + 2 >= height:
                continue
            if is_open3x3(grid, tx, ty):
                return True
    return False


def add_loops(
    grid: list[list[int]],
    blocked: set[tuple[int, int]],
    count: int,
) -> None:
    candidates = wall_candidates(grid, blocked)
    random.shuffle(candidates)
    breaked = 0
    for x, y, direction in candidates:
        if breaked >= count:
            return
        remove_wall(grid, x, y, direction)
        if makes_open_area(grid, x, y):
            add_wall(grid, x, y, direction)
            print(f"\n{render_maze(grid)}") # ! test
            pass
        else:
            breaked += 1
