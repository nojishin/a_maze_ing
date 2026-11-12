import sys


def error_handler(error: Exception) -> None:
    """Print the error message and exit with status 1.

    Args:
        error: The exception to report.

    """
    sys.exit(str(error))
