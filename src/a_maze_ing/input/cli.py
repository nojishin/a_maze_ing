import sys
from pathlib import Path

from a_maze_ing.errors.exceptions import InvalidArgumentsCountError

EXPECTED_ARGC = 2


def get_config_path() -> Path:
    argv_len = len(sys.argv)
    if argv_len != EXPECTED_ARGC:
        raise InvalidArgumentsCountError(argv_len)
    return Path(sys.argv[1])
