from pydantic import ValidationError

from .generate.gen_maze import generate
from .errors import ParamsValidationError
from .models import MazeParams


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

    def generate(self) -> list[list[int]]:
        print("generate called")  # ! for dev
        result = generate(self._params)
        print(result)
