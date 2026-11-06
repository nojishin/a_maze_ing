NORTH_BIT = 0
EAST_BIT = 1
SOUTH_BIT = 2
WEST_BIT = 3

WALL = "\033[47m  \033[0m"
SPACE = "  "
ENTRY = "\033[42m  \033[0m"
EXIT = "\033[41m  \033[0m"
PATH = "\033[46m  \033[0m"


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

    return h_wall, v_wall


def _draw_walls(grid: list[list[int]]) -> list[list[str]]:
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
            if h_wall[row][col]:
                canvas[2 * row][2 * col + 1] = WALL

    for row in range(height):
        for col in range(width + 1):
            if v_wall[row][col]:
                canvas[2 * row + 1][2 * col] = WALL
    return canvas


def _draw_markers(
    canvas: list[list[str]],
    entry: tuple[int, int],
    exit: tuple[int, int],  # noqa: A002 - pairs with `entry`
    path: list[tuple[int, int]] | None,
) -> None:
    if path is not None:
        for x, y in path:
            canvas[1 + y * 2][1 + x * 2] = PATH

    enx, eny = entry
    canvas[1 + eny * 2][1 + enx * 2] = ENTRY
    eix, eiy = exit
    canvas[1 + eiy * 2][1 + eix * 2] = EXIT


def _add_labels(canvas: list[list[str]]) -> str:
    lines = []

    grid_y = 0
    height = len(canvas) // 2
    digit_row_size = len(str(height))
    for i, r in enumerate(canvas):
        label = ""
        if i % 2 == 1:
            label = f"{grid_y!s:>{digit_row_size}} "
            grid_y += 1
        else:
            label = " " * (digit_row_size + 1)
        lines.append(label + "".join(r))

    digit_col_size = 2
    label = " " * (digit_row_size + 1)
    grid_x = 0
    for i in range(len(canvas[0])):
        if i % 2 == 1:
            label += f"{(grid_x % 100)!s:<{digit_col_size}}"
            grid_x += 1
        else:
            label += " " * (digit_col_size)

    label += "\n"
    return label + "\n".join(lines)


def render_maze(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],  # noqa: A002 - pairs with `entry`
    path: list[tuple[int, int]] | None = None,
) -> str:
    """Render the maze as a string with ANSI colors.

    Row and column numbers are drawn along the edges.

    Args:
        grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
        entry: The ``(x, y)`` entry cell.
        exit: The ``(x, y)`` exit cell.
        path: Cells of the solution path to draw, or ``None`` to hide it.

    Returns:
        The rendered maze.

    """
    canvas = _draw_walls(grid)
    _draw_markers(canvas, entry, exit, path)
    return _add_labels(canvas)
