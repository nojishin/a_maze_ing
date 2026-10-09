NORTH_BIT = 0
EAST_BIT = 1
SOUTH_BIT = 2
WEST_BIT = 3

WALL = "033[47m  \033[0m"
SPACE = "  "



def _build_wall_grids(
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

    print("h_wall:\n", h_wall)
    print("v_wall:\n", v_wall)

    return h_wall, v_wall


def render_maze(grid: list[list[int]]) -> str:
    height = len(grid)
    width = len(grid[0])
    h_wall, v_wall = _build_wall_grids(grid)
    canvas = [[SPACE] * (2 * width + 1) for _ in range(2 * height + 1)]

    for row in range(height + 1):
        for col in range(width + 1):
            up = row > 0 and v_wall[row - 1][col]
            down = row < height and v_wall[row][col]
            left = col > 0 and h_wall[row][col - 1]
            right = col < width and h_wall[row][col]
            mask = up | down | left | right
            if mask:
                canvas[2 * row][2 * col] = WALL

    for row in range(height + 1):
        for col in range(width):
            canvas[2 * row][2 * col + 1] = (
                WALL if h_wall[row][col] else SPACE
            )

    for row in range(height):
        for col in range(width + 1):
            canvas[2 * row + 1][2 * col] = (
                WALL if v_wall[row][col] else SPACE
            )

    return "\n".join("".join(row) for row in canvas)
