import sys
from pathlib import Path

from errors.exceptions import InvalidArgumentsCountError

EXPECTED_ARGC = 2


def get_config_path() -> Path:
    """Get the config file path from the command line.

    Returns:
        The path given as the only argument.

    Raises:
        InvalidArgumentsCountError: If there is not exactly one argument.

    """
    argv_len = len(sys.argv)
    if argv_len != EXPECTED_ARGC:
        raise InvalidArgumentsCountError(argv_len - 1)
    return Path(sys.argv[1])
