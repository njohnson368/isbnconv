import argparse
import sys

from .core import convert


def _lines_from(path):
    if path == "-":
        yield from sys.stdin
    else:
        with open(path, "r", encoding="utf-8") as f:
            yield from f


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="isbnconv",
        description="Convert ISBN-10 <-> ISBN-13, one ISBN per line.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=["-"],
        help="files to read (default: stdin). Use '-' explicitly for stdin.",
    )
    args = parser.parse_args(argv)

    had_error = False
    for path in args.files:
        for raw_line in _lines_from(path):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                print(f"{line} -> {convert(line)}")
            except ValueError as exc:
                had_error = True
                print(f"{line}: {exc}", file=sys.stderr)

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
