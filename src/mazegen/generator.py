import random

from pydantic import ValidationError

from .errors import MazeNotGeneratedError, ParamsValidationError
from .generate.gen_maze import generate
from .generate.pattern42 import MIN_HEIGHT, MIN_WIDTH
from .models import MazeParams, PathResult
from .solve.solver import solve


class MazeGenerator:
    """Generate a maze and find its solution path."""

    def __init__(  # noqa: PLR0913 - public API, mirrors MazeParams fields
        self,
        *,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],  # noqa: A002 - pairs with `entry`
        is_perfect: bool,
        seed: int | None = None,
    ) -> None:
        """Validate and store the maze parameters.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            entry: The ``(x, y)`` entry cell.
            exit: The ``(x, y)`` exit cell.
            is_perfect: Whether exactly one path joins any two cells.
            seed: Random seed. The same seed gives the same sequence of
                mazes. ``None`` gives a different sequence each time.

        Raises:
            ParamsValidationError: If a parameter is invalid.

        """
        try:
            self._params = MazeParams(
                width=width,
                height=height,
                entry=entry,
                exit=exit,
                is_perfect=is_perfect,
                seed=seed,
            )
            self._rnd = random.Random(self._params.seed)
        except ValidationError as e:
            raise ParamsValidationError(e) from e
        self._grid: list[list[int]] | None = None

    def generate(self) -> list[list[int]]:
        """Generate a new maze.

        Each call continues the generator's random sequence, so calling it
        again gives a different maze, even with a seed.

        Returns:
            A grid of wall bitmasks, indexed as ``grid[y][x]``.

        """
        self._grid = generate(self._params, self._rnd)
        return self._grid

    def solve(self) -> PathResult:
        """Find the shortest path from the entry to the exit.

        Returns:
            The path cells and directions.

        Raises:
            MazeNotGeneratedError: If ``generate()`` has not been called.
            PathNotFoundError: If the exit cannot be reached.

        """
        if self._grid is None:
            raise MazeNotGeneratedError
        return solve(self._grid, self._params.entry, self._params.exit)

    def has_42pattern(self) -> bool:
        """Check whether the maze is large enough to embed the 42 pattern.

        Returns:
            ``True`` if the width and height meet the minimum size for
            the 42 pattern, ``False`` otherwise.

        """
        if self._grid is None:
            raise MazeNotGeneratedError
        return (
            self._params.width >= MIN_WIDTH
            and self._params.height >= MIN_HEIGHT
        )
