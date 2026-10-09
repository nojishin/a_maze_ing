import random
from collections import deque
from errors.exceptions import MazeError

N = 0b0001
E = 0b0010
S = 0b0100
W = 0b1000

MOVES = {N: (0, -1, S), E: (1, 0, W), S: (0, 1, N), W: (-1, 0, E)}

PATTERN = [
    "X...XXX",
    "X.....X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX",
]


def make_blocked(width: int, height: int) -> set[tuple[int, int]]:
    if width < 9 or height < 7:
        return set()
    offset_x = (width - 7) // 2
    offset_y = (height - 5) // 2
    blocked: set[tuple[int, int]] = set()
    for j, line in enumerate(PATTERN):
        for i, char in enumerate(line):
            if char == "X":
                blocked.add((offset_x + i, offset_y + j))
    return blocked


def close_blocked(grid: list[list[int]], blocked: set[tuple[int, int]]) -> None:
    for x, y in blocked:
        for direction in MOVES:
            add_wall(grid, x, y, direction)


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


def remove_wall(grid: list[list[int]], x: int, y: int, direction: int) -> None:
    grid[y][x] &= ~direction
    dx, dy, opposite = MOVES[direction]
    grid[y + dy][x + dx] &= ~opposite


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
    if width < 2 or height < 2:
        return
    is_horizontal = choose_orientation(width, height)
    if is_horizontal:
        divide_horizontal(grid, x, y, width, height)
    else:
        divide_vertical(grid, x, y, width, height)


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



def generate(maze_params: MazeParams) -> list[list[int]]:
    width = 20
    height = 20
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
