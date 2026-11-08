"""Debug renderer that highlights wall changes between two mazes."""

from visualizer.renderder import (
    WALL,
    _add_labels,
    _draw_markers,
    _draw_walls,
)

ADDED = "\033[45m  \033[0m"  # magenta: wall that was added
REMOVED = "\033[43m  \033[0m"  # yellow: wall that was removed

Coord = tuple[int, int]


def render_diff(
    before: list[list[int]],
    after: list[list[int]],
    entry: Coord | None = None,
    exit: Coord | None = None,  # noqa: A002 - pairs with `entry`
    path: list[Coord] | None = None,
) -> str:
    """Render ``after`` with walls that differ from ``before`` highlighted.

    Added walls are drawn in magenta, removed walls in yellow, including
    corners. A summary line with the number of changed wall segments is added
    at the end.

    Args:
        before: Maze grid before the change, indexed as ``grid[y][x]``.
        after: Maze grid after the change, same size as ``before``.
        entry: The ``(x, y)`` entry cell, or ``None`` to not draw it.
        exit: The ``(x, y)`` exit cell, or ``None`` to not draw it.
        path: Cells of the solution path to draw, or ``None`` to hide it.

    Returns:
        The rendered maze.

    Raises:
        ValueError: If the two grids have different sizes.

    """
    if len(before) != len(after) or len(before[0]) != len(after[0]):
        msg = "grids must have the same size"
        raise ValueError(msg)

    old_canvas = _draw_walls(before)
    canvas = _draw_walls(after)
    added = removed = 0

    # Compare the drawn mazes cell by cell, so corners are caught too.
    for row, (old_line, new_line) in enumerate(
        zip(old_canvas, canvas, strict=True),
    ):
        for col, (old, new) in enumerate(zip(old_line, new_line, strict=True)):
            if old == new:
                continue
            canvas[row][col] = ADDED if new == WALL else REMOVED
            # Count wall segments only: corners sit at (even, even).
            if row % 2 == 0 and col % 2 == 0:
                continue
            if new == WALL:
                added += 1
            else:
                removed += 1

    _draw_markers(canvas, entry, exit, path)

    summary = f"\n{ADDED} added: {added}  {REMOVED} removed: {removed}"
    return _add_labels(canvas) + summary


class DiffPrinter:
    """Print a maze, highlighting changes since the previous call.

    Usage::

        dp = DiffPrinter()
        dp.show(grid)  # first call: plain maze
        remove_wall(grid, x, y, direction)
        dp.show(grid)  # removed wall shown in yellow

    With ``skip_unchanged=True``, calls where the maze has not changed since
    the last call print nothing.
    """

    def __init__(self, *, skip_unchanged: bool = False) -> None:
        """Start with no previous maze and no entry or exit.

        Args:
            skip_unchanged: Print nothing when the maze has not changed since
                the last call. The first call always prints.

        """
        self.skip_unchanged = skip_unchanged
        self._prev: list[list[int]] | None = None
        self.entry: Coord | None = None
        self.exit: Coord | None = None

    def reset(
        self,
        entry: Coord | None = None,
        exit: Coord | None = None,  # noqa: A002 - pairs with `entry`
    ) -> None:
        """Forget the previous maze, so the next call prints it plain.

        Args:
            entry: The ``(x, y)`` entry cell to draw, or ``None`` to hide it.
            exit: The ``(x, y)`` exit cell to draw, or ``None`` to hide it.

        """
        self._prev = None
        self.entry = entry
        self.exit = exit

    def show(self, grid: list[list[int]], label: str = "") -> None:
        """Print ``grid`` diffed against the last shown grid.

        Args:
            grid: Maze grid of wall bitmasks, indexed as ``grid[y][x]``.
            label: Optional heading printed above the maze.

        """
        if self.skip_unchanged and self._prev == grid:
            return
        if label:
            print(f"--- {label} ---")
        before = self._prev if self._prev is not None else grid
        print(render_diff(before, grid, self.entry, self.exit))
        # Copy so later in-place edits to `grid` don't change our snapshot.
        self._prev = [row[:] for row in grid]


# Shared instance so debug output from different modules diffs in sequence.
debug_printer = DiffPrinter(skip_unchanged=True)
