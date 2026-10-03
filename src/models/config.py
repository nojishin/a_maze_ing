from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator

MazeSize = Annotated[int, Field(ge=1, le=100)]
MazeCoord = Annotated[int, Field(ge=0, le=99)]


def parse_coord(value: str) -> tuple[int, int]:
    x, sep, y = value.partition(",")
    if not sep:
        msg = "expected format 'x,y'"
        raise ValueError(msg)
    return (int(x), int(y))


MazePoint = Annotated[tuple[MazeCoord, MazeCoord], BeforeValidator(parse_coord)]


class Config(BaseModel):
    model_config = ConfigDict(alias_generator=str.upper, extra="forbid")
    width: MazeSize
    height: MazeSize
    entry: MazePoint
    exit: MazePoint
    output_file: str
    is_perfect: bool = Field(alias="PERFECT")

    @model_validator(mode="after")
    def check_entry_exit_differ(self) -> Self:
        if self.entry == self.exit:
            msg = "ENTRY and EXIT must be different"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def check_entry_exit_in_bounds(self) -> Self:
        def _is_out_of_range(size: int, value: int) -> bool:
            return size <= value

        def _is_out_of_bounds(
            width: int,
            height: int,
            point: tuple[int, int],
        ) -> bool:
            x, y = point
            return _is_out_of_range(width, x) or _is_out_of_range(height, y)

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
                f"EXIT {self.exit!s} is outside the maze ({self.width}x{self.height})",
            )
        if errors:
            raise ValueError(", ".join(errors))
        return self
