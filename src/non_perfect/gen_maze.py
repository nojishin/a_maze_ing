import random

from models import Config

N = 0b0001
E = 0b0010
S = 0b0100
W = 0b1000

MOVES = {N: (0, -1, S), E: (1, 0, W), S: (0, 1, N), W: (-1, 0, E)}


def add_wall(grid, x, y, direction) -> None:
    grid[x][y] |= direction
    dx, dy, opposite = MOVES[direction]
    grid[x + dx][y + dy] |= opposite


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
    divide()


def divide_vertical(
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    divide()


def divide(
    grid: list[list[int]],
    x,
    y,
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


def generate(config: Config) -> str:
    width = config.width
    height = config.height
    grid = parse_grid()
    blocked: set[tuple[int, int]] = set()
    divide(width, height, 0, 0, grid, blocked)
    return ""
