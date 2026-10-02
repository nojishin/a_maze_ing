from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator

MazeSize = Annotated[int, Field(ge=1, le=100)]
MazeCoord = Annotated[int, Field(ge=0, le=99)]


def parse_coord(value: str) -> tuple[int, int]:
    x, sep, y = value.partition(",")
    if not sep:
        raise ValueError
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
            raise ValueError
        return self
