import sys
from pathlib import Path

from a_maze_ing.errors.exceptions import InvalidArgumentsCountError


def get_config_path() -> Path:
    print(sys.argv, len(sys.argv))  # ! test
    argv_len = len(sys.argv)
    if argv_len != 2:
        raise InvalidArgumentsCountError(argv_len)
    


get_config_path()
