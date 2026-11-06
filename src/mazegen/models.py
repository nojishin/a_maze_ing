from dataclasses import dataclass
from typing import Annotated, Self

from pydantic import BaseModel, Field, model_validator

MazeSize = Annotated[int, Field(ge=1, le=100)]
MazeCoord = Annotated[int, Field(ge=0, le=99)]


class MazeParams(BaseModel):
    """Validated parameters of a maze."""

    width: MazeSize
    height: MazeSize
    entry: tuple[MazeCoord, MazeCoord]
    exit: tuple[MazeCoord, MazeCoord]
    is_perfect: bool
    seed: int | None = None

    @model_validator(mode="after")
    def check_entry_exit_differ(self) -> Self:
        """Check that the entry and the exit are different cells.

        Raises:
            ValueError: If they are the same cell.

        """
        if self.entry == self.exit:
            msg = "ENTRY and EXIT must be different"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def check_entry_exit_in_bounds(self) -> Self:
        """Check that the entry and the exit are inside the maze.

        Raises:
            ValueError: If either one is outside the maze.

        """
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


@dataclass
class PathResult:
    """Solution path of a maze.

    Attributes:
        coord: The ``(x, y)`` cells of the path, from entry to exit.
        directions: The moves of the path as ``N``, ``E``, ``S`` and ``W``.

    """

    coord: list[tuple[int, int]]
    directions: str
