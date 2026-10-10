from .maze_utils import MOVES, add_wall
from visualizer.renderder import render_maze

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
            print(f"\n{render_maze(grid)}")  # ! test
            pass
