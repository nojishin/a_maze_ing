N = 0b0001
E = 0b0010
S = 0b0100
W = 0b1000

MOVES = {N: (0, -1, S), E: (1, 0, W), S: (0, 1, N), W: (-1, 0, E)}


def add_wall(grid: list[list[int]], x: int, y: int, direction: int) -> None:
    grid[y][x] |= direction
    dx, dy, opposite = MOVES[direction]
    grid[y + dy][x + dx] |= opposite


def remove_wall(grid: list[list[int]], x: int, y: int, direction: int) -> None:
    grid[y][x] &= ~direction
    dx, dy, opposite = MOVES[direction]
    grid[y + dy][x + dx] &= ~opposite
