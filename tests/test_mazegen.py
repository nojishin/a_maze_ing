"""Unit tests for MazeGenerator, focused on edge cases."""

from dataclasses import asdict
from typing import Any

import pytest

from mazegen import (
    MazeGenerator,
    MazeNotGeneratedError,
    ParamsValidationError,
    PatternOverlapError,
)
from mazegen.generate.pattern42 import MIN_HEIGHT, MIN_WIDTH, make_blocked
from tests.checks import Params, count_open_edges, maze_errors


def make(p: Params) -> MazeGenerator:
    """Build a MazeGenerator from Params."""
    return MazeGenerator(**asdict(p))


def build(**overrides: Any) -> MazeGenerator:  # noqa: ANN401 - kwargs
    """Build a MazeGenerator from default args with some overridden."""
    kwargs: dict[str, Any] = {
        "width": 20,
        "height": 15,
        "entry": (0, 0),
        "exit": (19, 14),
        "is_perfect": True,
        "seed": 42,
    }
    kwargs.update(overrides)
    return MazeGenerator(**kwargs)


# --- valid mazes ---------------------------------------------------------


@pytest.mark.parametrize("is_perfect", [True, False])
@pytest.mark.parametrize(
    ("width", "height", "entry", "exit_"),
    [
        (3, 3, (0, 0), (2, 2)),  # smallest, could be fully open
        (3, 100, (0, 0), (2, 99)),  # narrowest and tallest
        (100, 3, (99, 0), (0, 2)),  # widest and lowest
        (3, 3, (1, 1), (0, 0)),  # entry in the center
        (MIN_WIDTH - 1, MIN_HEIGHT, (0, 0), (7, 6)),  # just too small for 42
        (MIN_WIDTH, MIN_HEIGHT - 1, (0, 0), (8, 5)),  # just too small for 42
        (MIN_WIDTH, MIN_HEIGHT, (0, 0), (8, 6)),  # smallest with 42
        (100, 100, (0, 0), (99, 99)),  # largest
        (20, 15, (1, 1), (2, 1)),  # adjacent entry and exit
    ],
)
def test_valid_maze(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    *,
    is_perfect: bool,
) -> None:
    """Generated maze passes every check for edge-case sizes."""
    p = Params(width, height, entry, exit_, is_perfect, seed=0)
    gen = make(p)
    grid = gen.generate()
    assert maze_errors(grid, p, gen.solve()) == []


@pytest.mark.parametrize(
    ("width", "height", "expected"),
    [
        (MIN_WIDTH, MIN_HEIGHT, True),
        (MIN_WIDTH - 1, MIN_HEIGHT, False),
        (MIN_WIDTH, MIN_HEIGHT - 1, False),
        (100, 100, True),
    ],
)
def test_has_42pattern(width: int, height: int, *, expected: bool) -> None:
    """has_42pattern reflects whether the maze is large enough."""
    gen = build(width=width, height=height, exit=(width - 1, height - 1))
    gen.generate()
    assert gen.has_42pattern() is expected
    assert bool(make_blocked(width, height)) is expected


# --- seed ----------------------------------------------------------------


@pytest.mark.parametrize("is_perfect", [True, False])
def test_same_seed_same_maze(*, is_perfect: bool) -> None:
    """The same seed gives the same maze."""
    a = build(seed=123, is_perfect=is_perfect).generate()
    b = build(seed=123, is_perfect=is_perfect).generate()
    assert a == b


def test_regenerate_with_seed_differs() -> None:
    """Calling generate() twice on one seeded generator gives new mazes."""
    gen = build(seed=7)
    assert gen.generate() != gen.generate()


def test_regenerate_sequence_is_reproducible() -> None:
    """Two generators with the same seed give the same sequence of mazes."""
    a = build(seed=7)
    b = build(seed=7)
    assert [a.generate() for _ in range(3)] == [b.generate() for _ in range(3)]


def test_different_seeds_differ() -> None:
    """Different seeds give different mazes."""
    grids = {
        tuple(map(tuple, build(width=30, height=30, exit=(29, 29), seed=s)
                  .generate()))
        for s in range(5)
    }
    assert len(grids) > 1


def test_no_seed_is_random() -> None:
    """Without a seed, generate() gives different mazes."""
    gen = build(width=30, height=30, exit=(29, 29), seed=None)
    grids = {tuple(map(tuple, gen.generate())) for _ in range(5)}
    assert len(grids) > 1


def test_imperfect_has_loops() -> None:
    """A non-perfect maze has more open edges than a spanning tree."""
    p = Params(30, 30, (0, 0), (29, 29), is_perfect=False, seed=1)
    grid = make(p).generate()
    cells = p.width * p.height - len(make_blocked(p.width, p.height))
    assert count_open_edges(grid) > cells - 1


# --- errors --------------------------------------------------------------


@pytest.mark.parametrize(
    "overrides",
    [
        {"width": 0},
        {"width": 2},  # just below the minimum
        {"width": 101},
        {"height": 0},
        {"height": 2},  # just below the minimum
        {"height": 101},
        {"width": 2, "height": 2, "exit": (1, 1)},
        {"width": -1},
        {"entry": (-1, 0)},
        {"exit": (0, -1)},
        {"entry": (20, 0)},  # x == width
        {"exit": (0, 15)},  # y == height
        {"entry": (19, 14)},  # same as exit
        {"width": "abc"},
        {"entry": (1, 2, 3)},
    ],
)
def test_invalid_params(overrides: dict[str, Any]) -> None:
    """Invalid params raise ParamsValidationError."""
    with pytest.raises(ParamsValidationError):
        build(**overrides)


@pytest.mark.parametrize("field", ["entry", "exit"])
def test_entry_or_exit_on_pattern(field: str) -> None:
    """generate() raises if entry or exit is on the 42 pattern."""
    cell = next(iter(make_blocked(20, 15)))
    gen = build(**{field: cell})
    with pytest.raises(PatternOverlapError):
        gen.generate()


def test_solve_before_generate() -> None:
    """solve() before generate() raises MazeNotGeneratedError."""
    with pytest.raises(MazeNotGeneratedError):
        build().solve()


def test_has_42pattern_before_generate() -> None:
    """has_42pattern() before generate() raises MazeNotGeneratedError."""
    with pytest.raises(MazeNotGeneratedError):
        build().has_42pattern()
