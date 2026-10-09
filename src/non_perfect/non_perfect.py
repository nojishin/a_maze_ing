import random

from .maze_utils import E, MOVES, S, add_wall, remove_wall


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
            if is_open3x3(grid, tx, ty) and all(
                (tx >= 0, tx + 2 < width, ty + 2 < height, ty >= 0),
            ):
                return True
    return False


def add_loops(grid:list[list[int]],blocked:set(tupe(int,int)), count)->None:
    candidates = wall_candidates(grid,blocked)
    random.shuffle(candidates)
    breaked = 0
    for sell in candidates:
        x,y,direction = sell
        remove_wall(grid,x,y,direction)
        if makes_open_area(grid,x,y):
            add_wall(grid,x,y,direction)
        else:
            breaked += 1
        if count == blocked:
            return
    return
