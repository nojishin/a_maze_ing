import sys


def error_handler(error: Exception) -> None:
    print(str(error))
    sys.exit(1)
