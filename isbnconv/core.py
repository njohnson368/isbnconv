"""ISBN-10 / ISBN-13 checksum math and conversion.

ISBN-10 and ISBN-13 encode the same book identifier but under two different
check digit algorithms (mod 11 with positional weights 10..2, vs mod 10 with
alternating weights 1/3). Converting between them means re-deriving the check
digit, not just reformatting the string.
"""


def clean(raw: str) -> str:
    """Strip hyphens/spaces and normalize case (the ISBN-10 check digit can be 'X')."""
    return raw.strip().replace("-", "").replace(" ", "").upper()


def isbn10_check_digit(digits9: str) -> str:
    if len(digits9) != 9 or not digits9.isdigit():
        raise ValueError(f"expected 9 digits, got {digits9!r}")
    total = sum((10 - i) * int(d) for i, d in enumerate(digits9))
    remainder = total % 11
    check = (11 - remainder) % 11
    return "X" if check == 10 else str(check)


def isbn13_check_digit(digits12: str) -> str:
    if len(digits12) != 12 or not digits12.isdigit():
        raise ValueError(f"expected 12 digits, got {digits12!r}")
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits12))
    check = (10 - (total % 10)) % 10
    return str(check)


def is_valid_isbn10(raw: str) -> bool:
    isbn = clean(raw)
    if len(isbn) != 10 or not isbn[:9].isdigit():
        return False
    if not (isbn[9].isdigit() or isbn[9] == "X"):
        return False
    return isbn10_check_digit(isbn[:9]) == isbn[9]


def is_valid_isbn13(raw: str) -> bool:
    isbn = clean(raw)
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    return isbn13_check_digit(isbn[:12]) == isbn[12]


def isbn10_to_isbn13(raw: str) -> str:
    isbn = clean(raw)
    if not is_valid_isbn10(isbn):
        raise ValueError(f"not a valid ISBN-10: {raw!r}")
    digits12 = "978" + isbn[:9]
    return digits12 + isbn13_check_digit(digits12)


def isbn13_to_isbn10(raw: str) -> str:
    isbn = clean(raw)
    if not is_valid_isbn13(isbn):
        raise ValueError(f"not a valid ISBN-13: {raw!r}")
    if not isbn.startswith("978"):
        # 979-prefixed ISBN-13s (and any future Bookland prefix) have no
        # ISBN-10 form, since ISBN-10 space only ever mapped the 978 range.
        raise ValueError(f"ISBN-13 {raw!r} has no ISBN-10 equivalent (prefix != 978)")
    digits9 = isbn[3:12]
    return digits9 + isbn10_check_digit(digits9)


def convert(raw: str) -> str:
    """Convert an ISBN to the other format, auto-detecting which format it's in."""
    isbn = clean(raw)
    if len(isbn) == 10:
        return isbn10_to_isbn13(isbn)
    if len(isbn) == 13:
        return isbn13_to_isbn10(isbn)
    raise ValueError(f"expected 10 or 13 characters after cleanup, got {len(isbn)}: {raw!r}")
