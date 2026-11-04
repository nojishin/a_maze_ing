from pydantic import ValidationError

from .errors import MazeNotGeneratedError, ParamsValidationError
from .generate.gen_maze import generate
from .models import MazeParams, PathResult
from .solve.solver import solve


class MazeGenerator:
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
        try:
            self._params = MazeParams(
                width=width,
                height=height,
                entry=entry,
                exit=exit,
                is_perfect=is_perfect,
                seed=seed,
            )
        except ValidationError as e:
            raise ParamsValidationError(e) from e
        self._grid: list[list[int]] | None = None

    def generate(self) -> list[list[int]]:
        self._grid = generate(self._params)
        return self._grid

    def solve(self) -> PathResult:
        if self._grid is None:
            raise MazeNotGeneratedError
        return solve(self._grid, self._params.entry, self._params.exit)
