import random

from ..errors import MazeError
from ..models import Config


def choose_orientation(width: int, height: int) -> bool:
    if width < height:
        return True
    if width > height:
        return False
    return random.choice([True, False])


def parse_grid(width: int, height: int) -> list[list[int]]:
    top = [0b10001] + [0b1000] * (width - 2) + [0b1100]
    middle = [0b0001] + [0b0000] * (width - 2) + [0b0100]
    bottom = [0b0011] + [0b0010] * (width - 2) + [0b0110]
    return top + middle * (height - 2) + bottom


def divide_horizontal() -> None:
    pass


def divide_vertical() -> None:
    pass


def divide(width: int, height: int, grid: list[list[int]]) -> None:
    is_horizontal = choose_orientation(width, height)
    if is_horizontal:
        pass
    else:
        pass


def generate(config: Config) -> str:
    width = config.width
    height = config.height
    grid = parse_grid()
    divide(width, height, grid)
    return ""
