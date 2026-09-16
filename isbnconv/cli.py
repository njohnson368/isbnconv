import argparse
import sys

from .core import convert, is_valid


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
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="report valid/invalid for each ISBN instead of converting it",
    )
    args = parser.parse_args(argv)

    had_error = False
    for path in args.files:
        try:
            for raw_line in _lines_from(path):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if args.validate_only:
                    if is_valid(line):
                        print(f"{line}: valid")
                    else:
                        had_error = True
                        print(f"{line}: invalid")
                    continue
                try:
                    print(f"{line} -> {convert(line)}")
                except ValueError as exc:
                    had_error = True
                    print(f"{line}: {exc}", file=sys.stderr)
        except OSError as exc:
            had_error = True
            print(f"{path}: {exc.strerror or exc}", file=sys.stderr)

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
