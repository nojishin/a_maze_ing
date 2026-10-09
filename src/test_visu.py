import sys
from pathlib import Path


NORTH_BIT = 0
EAST_BIT = 1
SOUTH_BIT = 2
WEST_BIT = 3

# 交点(corner)に集まる上下左右の線の有無 -> 罫線文字
# ビットは (up, right, down, left) の順で立てる
CORNER_CHARS = {
    0b0000: " ",
    0b0001: "╵",
    0b0010: "╶",
    0b0011: "└",
    0b0100: "╷",
    0b0101: "│",
    0b0110: "┌",
    0b0111: "├",
    0b1000: "╴",
    0b1001: "┘",
    0b1010: "─",
    0b1011: "┴",
    0b1100: "┐",
    0b1101: "┤",
    0b1110: "┬",
    0b1111: "┼",
}


class MazeFormatError(Exception):
    def __init__(self, msg: str = "The maze was not generated correctly."):
        super().__init__(msg)


def parse_hex_grid(file_path: Path) -> list[list[int]]:
    with file_path.open() as f:
        lines: list[str] = []
        for raw_line in f:
            line = raw_line.strip("\n")
            if line == "":
                break
            lines.append(line)
    if not lines:
        raise MazeFormatError

    width = len(lines[0])
    grid: list[list[int]] = []

    for i, line in enumerate(lines):
        if len(line) != width:
            raise MazeFormatError
        try:
            row = [int(char, 16) for char in line]
        except ValueError:
            raise ValueError
        else:
            grid.append(row)
    return grid


def build_wall_grids(
    grid: list[list[int]],
) -> tuple[list[list[bool]], list[list[bool]]]:
    height = len(grid)
    width = len(grid[0])
    h_wall = [[False] * width for _ in range(height + 1)]
    v_wall = [[False] * (width + 1) for _ in range(height)]

    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            if cell & (1 << NORTH_BIT):
                h_wall[y][x] = True
            if cell & (1 << EAST_BIT):
                v_wall[y][x + 1] = True
            if cell & (1 << SOUTH_BIT):
                h_wall[y + 1][x] = True
            if cell & (1 << WEST_BIT):
                v_wall[y][x] = True

    return h_wall, v_wall


def render_maze(grid: list[list[int]]) -> str:
    height = len(grid)
    width = len(grid[0])
    h_wall, v_wall = build_wall_grids(grid)
    canvas = [[" "] * (2 * width + 1) for _ in range(2 * height + 1)]

    for row in range(height + 1):
        for col in range(width + 1):
            up = row > 0 and v_wall[row - 1][col]
            down = row < height and v_wall[row][col]
            left = col > 0 and h_wall[row][col - 1]
            right = col < width and h_wall[row][col]
            mask = up << 0 | right << 1 | down << 2 | left << 3
            canvas[2 * row][2 * col] = CORNER_CHARS[mask]

    for row in range(height + 1):
        for col in range(width):
            canvas[2 * row][2 * col + 1] = "─" if h_wall[row][col] else " "

    for row in range(height):
        for col in range(width + 1):
            canvas[2 * row + 1][2 * col] = "│" if v_wall[row][col] else " "

    return "\n".join("".join(row) for row in canvas)
