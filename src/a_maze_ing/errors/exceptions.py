class MazeError(Exception): ...


class InvalidArgumentsCountError(MazeError):
    def __init__(self, count: int) -> None:
        super().__init__(
            "(Usage: python3 a_maze_ing.py <config_file>\n"
            f"Expected 1 argument, but got {count}",
        )
