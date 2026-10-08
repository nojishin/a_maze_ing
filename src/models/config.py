from pathlib import Path
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    model_validator,
)

MazeSize = Annotated[int, Field(ge=1, le=100)]
MazeCoord = Annotated[int, Field(ge=0, le=99)]


def _parse_coord(value: str) -> tuple[int, int]:
    x, sep, y = value.partition(",")
    msg = "Input should be two integers in the format 'x,y'"
    if not sep:
        raise ValueError(msg)
    try:
        int_x = int(x)
        int_y = int(y)
    except ValueError as e:
        raise ValueError(msg) from e
    return (int_x, int_y)


MazePoint = Annotated[
    tuple[MazeCoord, MazeCoord],
    BeforeValidator(_parse_coord),
]


def _parse_output_file(value: str) -> str:
    if not value:
        msg = "Input should not be empty"
        raise ValueError(msg)
    return value


class Config(BaseModel):
    model_config = ConfigDict(alias_generator=str.upper, extra="forbid")

    width: MazeSize
    height: MazeSize
    entry: MazePoint
    exit: MazePoint
    output_file: Annotated[Path, BeforeValidator(_parse_output_file)]
    is_perfect: bool = Field(alias="PERFECT")
    seed: int | None = None

    @model_validator(mode="after")
    def check_entry_exit_differ(self) -> Self:
        if self.entry == self.exit:
            msg = "ENTRY and EXIT must be different"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def check_entry_exit_in_bounds(self) -> Self:
        def _is_out_of_bounds(
            width: int,
            height: int,
            point: tuple[int, int],
        ) -> bool:
            x, y = point
            return x >= width or y >= height

        errors: list[str] = []
        if _is_out_of_bounds(
            self.width,
            self.height,
            self.entry,
        ):
            errors.append(
                f"ENTRY {self.entry!s} is outside "
                f"the maze ({self.width}x{self.height})",
            )
        if _is_out_of_bounds(
            self.width,
            self.height,
            self.exit,
        ):
            errors.append(
                f"EXIT {self.exit!s} is outside the maze "
                f"({self.width}x{self.height})",
            )
        if errors:
            raise ValueError(", ".join(errors))
        return self
