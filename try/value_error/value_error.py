import sys
from pathlib import Path

FILE_PATH = Path("bad.txt")


def _read_config_file(path: Path) -> str:
    with open(path) as f:
        return f.read()


with open(FILE_PATH, "wb") as f:
    f.write(b"hello \xff\xfe world")


try:
    s = _read_config_file(FILE_PATH)
    print(s)
except ValueError as e:
    print("raise value error:", str(e))
