from models import MazeParams


class MazeGenerator:
    def __init__(
        self,
        height: int,
        width: int,
        entry: tuple[int, int],
        exit: tuple[int, int],  # noqa: A002 - pairs with `entry`
        seed: int | None = None,
    ) -> None:
        self._params = MazeParams(height, width, entry, exit, seed)

    def generate(self) -> None:
        pass
