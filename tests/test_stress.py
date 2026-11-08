"""Run MazeGenerator many times with random params and print stats.

Run with ``-s`` to see the stats.
"""

import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, field

import pytest

from mazegen import MazeGenerator
from tests.checks import Params, maze_errors, random_params

RUNS = 100


@dataclass
class RunResult:
    """Outcome of one run."""

    params: Params
    elapsed: float = 0.0
    path_len: int = 0
    errors: list[str] = field(default_factory=list)


def run_once(p: Params) -> RunResult:
    """Generate, solve and check one maze."""
    result = RunResult(params=p)
    try:
        gen = MazeGenerator(**asdict(p))
        start = time.perf_counter()
        grid = gen.generate()
        result.elapsed = time.perf_counter() - start
        path = gen.solve()
    except Exception:  # noqa: BLE001 - report any crash as a failure
        result.errors.append(traceback.format_exc().strip())
        return result
    result.errors = maze_errors(grid, p, path)
    result.path_len = len(path.directions)
    return result


@pytest.mark.parametrize(
    "perfect",
    [True, False],
    ids=["perfect", "imperfect"],
)
def test_random_stats(*, perfect: bool) -> None:
    """Every random maze is valid; print time and path length stats."""
    params = [random_params(perfect=perfect) for _ in range(RUNS)]
    # Processes, not threads: generate() seeds the global random module.
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(run_once, params))

    times = [r.elapsed * 1000 for r in results]
    lens = [r.path_len for r in results]
    print(f"\nrandom(perfect={perfect}) x {RUNS}")
    print(
        f"time(ms): min={min(times):.1f}, max={max(times):.1f}, "
        f"avg={sum(times) / len(times):.1f}",
    )
    print(
        f"path len: min={min(lens)}, max={max(lens)}, "
        f"avg={sum(lens) / len(lens):.1f}",
    )

    failed = [f"{r.params}\n  " + "\n  ".join(r.errors[:5])
              for r in results if r.errors]
    assert not failed, "\n".join(failed)
