"""Check generated output files with the provided maze_analyzer."""

from dataclasses import asdict
from pathlib import Path

import pytest

import maze_analyzer as ma
from a_maze_ing import write_file
from mazegen import MazeGenerator
from tests.checks import Params, random_params

RUNS = 100
# No real dead-end allowed: the analyzer's bonus-grade check.
BONUS_MAX_DEAD_ENDS = 0
EXPECTED = {True: "PERFECT maze", False: "Pac-Man-USABLE"}


def analyzer_verdict(p: Params, output_file: Path) -> str:
    """Generate a maze, write it like a_maze_ing does, return the verdict."""
    gen = MazeGenerator(**asdict(p))
    grid = gen.generate()
    path = gen.solve()
    write_file(
        output_file=output_file,
        grid=grid,
        entry=p.entry,
        exit=p.exit,
        directions=path.directions,
    )
    report = ma.analyze(ma.Maze.from_file(str(output_file)))
    return ma.verdict(report, ma.DEFAULT_MIN_LOOPS, BONUS_MAX_DEAD_ENDS)


@pytest.mark.parametrize("perfect", [True, False])
def test_default_config(tmp_path: Path, *, perfect: bool) -> None:
    """The config.txt settings pass the analyzer in both modes."""
    p = Params(
        width=20,
        height=15,
        entry=(0, 0),
        exit=(19, 14),
        is_perfect=perfect,
        seed=42,
    )
    verdict = analyzer_verdict(p, tmp_path / "maze.txt")
    assert verdict.startswith(EXPECTED[perfect]), verdict


@pytest.mark.parametrize(
    "perfect",
    [True, False],
    ids=["perfect", "imperfect"],
)
def test_random_mazes(tmp_path: Path, *, perfect: bool) -> None:
    """Random mazes get the expected analyzer verdict."""
    failed = []
    for i in range(RUNS):
        p = random_params(perfect=perfect)
        verdict = analyzer_verdict(p, tmp_path / f"maze{i}.txt")
        if not verdict.startswith(EXPECTED[perfect]):
            failed.append(f"{p}\n  {verdict}")
    assert not failed, "\n".join(failed)
