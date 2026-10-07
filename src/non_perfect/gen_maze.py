import random

from models import Config

N = 0b0001
E = 0b0010
S = 0b0100
W = 0b1000

MOVES = {N: (0, -1, S), E: (1, 0, W), S: (0, 1, N), W: (-1, 0, E)}


def add_wall(grid: list[list[int]], x: int, y: int, direction: int) -> None:
    grid[y][x] |= direction
    dx, dy, opposite = MOVES[direction]
    grid[y + dy][x + dx] |= opposite


def choose_orientation(width: int, height: int) -> bool:
    if width < height:
        return True
    if width > height:
        return False
    return random.choice([True, False])


def parse_grid(width: int, height: int) -> list[list[int]]:
    grid = [[0] * width for _ in range(height)]
    for x in range(width):
        grid[0][x] |= N
        grid[height - 1][x] |= S
    for y in range(height):
        grid[y][0] |= W
        grid[y][width - 1] |= E
    return grid


def divide_horizontal(
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    wall_y = y + random.randint(0, height - 2)
    passage_x = random.randint(x, x + width - 1)
    for col in range(x, x + width):
        if col == passage_x:
            continue
        add_wall(grid, col, wall_y, S)
    divide(grid, x, y, width, wall_y - y + 1)
    divide(grid, x, wall_y + 1, width, y + height - wall_y - 1)


def divide_vertical(
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    wall_x = x + random.randint(0, width - 2)
    passage_y = random.randint(y, y + height - 1)
    for row in range(y, y + height):
        if row == passage_y:
            continue
        add_wall(grid, wall_x, row, E)
    divide(grid, x, y, wall_x - x + 1, height)
    divide(grid, wall_x + 1, y, x + width - wall_x - 1, height)


def divide(
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    is_horizontal = choose_orientation(width, height)
    if width < 2 or height < 2:
        return
    if is_horizontal:
        divide_horizontal(grid, x, y, width, height)
    else:
        divide_vertical(grid, x, y, width, height)


def generate() -> list[list[int]]:
    width = 20
    height = 20
    grid = parse_grid(width,height)
    random.seed(42)
    divide(grid, 0, 0, width, height)
    return grid
