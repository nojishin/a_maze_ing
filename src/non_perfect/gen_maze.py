import random
from collections import deque

from errors.exceptions import MazeError
from visualizer.renderder import render_maze

from .maze_utils import E, MOVES, N, S, W, add_wall, remove_wall
from .non_perfect import add_loops
from .pattern42 import make_blocked


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


def flood(
    grid: list[list[int]],
    start: tuple[int, int],
    visited: set[tuple[int, int]],
) -> None:
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


def repair(grid: list[list[int]], blocked: set[tuple[int, int]]) -> None:
    visited: set[tuple[int, int]] = set()
    flood(grid, (0, 0), visited, blocked)
    while True:
        candidates = find_candidates(grid, visited, blocked)
        if not candidates:
            return
        x, y, direction = random.choice(candidates)
        remove_wall(grid, x, y, direction)
        dx, dy, _ = MOVES[direction]
        flood(grid, (x + dx, y + dy), visited, blocked)


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
        print(f"\n{render_maze(grid)}")  # ! test
        pass
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
        print(f"\n{render_maze(grid)}")  # ! test
        pass
    divide(grid, x, y, wall_x - x + 1, height)
    divide(grid, wall_x + 1, y, x + width - wall_x - 1, height)


def divide(
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    if width < 2 or height < 2:
        return
    is_horizontal = choose_orientation(width, height)
    if is_horizontal:
        divide_horizontal(grid, x, y, width, height)
    else:
        divide_vertical(grid, x, y, width, height)


def generate(maze_params: MazeParams) -> list[list[int]]:
    width = maze_params.width
    height = maze_params.height
    grid = parse_grid(width, height)
    blocked = make_blocked(width,height)
    if blocked == set():
        msg = "Unable to display 42 patterns."
        raise MazeError(msg)
    random.seed(maze_params.seed)
    divide(grid, 0, 0, width, height)
    repair(grid,blocked)
    if not maze_params.is_perfect:
        loop_ration = random.randint(10,30)
        count = width * height // loop_ration
        add_loops(grid,blocked,count)
    return grid
