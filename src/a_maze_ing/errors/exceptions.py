from pathlib import Path


class MazeError(Exception): ...


class InvalidArgumentsCountError(MazeError):
    def __init__(self, count: int) -> None:
        super().__init__(
            "(Usage: python3 a_maze_ing.py <config_file>\n"
            f"Expected 1 argument, but got {count}",
        )


class ConfigFileNotFoundError(MazeError):
    def __init__(self, file_path: Path) -> None:
        super().__init__(f"Config File not found: '{file_path}'")


class ConfigFileReadError(MazeError):
    def __init__(self, file_path: Path, reason: str) -> None:
        super().__init__(f"Failed to read config file '{file_path}': {reason}")
