# isbnconv

Every book has two ISBNs: the old 10-digit one and the 13-digit one that
replaced it in 2007 (which is also just an EAN-13 barcode with a `978` or
`979` "Bookland" prefix). They're not the same digits reformatted - each has
its own check digit computed with a different algorithm, so converting one to
the other means redoing the checksum math, not just adding/removing a prefix.

`isbnconv` reads ISBNs (one per line, either format, hyphens or spaces
optional) and prints each one converted to the other format.

## Usage

From a file:

```
$ cat books.txt
0-306-40615-2
978-0-13-468599-1
$ python -m isbnconv books.txt
0-306-40615-2 -> 9780306406157
978-0-13-468599-1 -> 0134685997
```

From stdin (no file argument, or `-`):

```
$ echo "0306406152" | python -m isbnconv
0306406152 -> 9780306406157
```

Invalid input is reported on stderr and doesn't stop the rest of the batch:

```
$ printf '0306406152\n1234567890\n' | python -m isbnconv
0306406152 -> 9780306406157
1234567890: not a valid ISBN-10: '1234567890'
```

Lines that are blank or start with `#` are skipped, so you can keep comments
in your input files.

Use `--validate-only` to check ISBNs without converting them:

```
$ printf '0306406152\n1234567890\n' | python -m isbnconv --validate-only
0306406152: valid
1234567890: invalid
```

## As a library

```python
from isbnconv import convert, is_valid, is_valid_isbn10, is_valid_isbn13

convert("0-306-40615-2")   # "9780306406157"
is_valid_isbn13("9780306406157")  # True
is_valid("9780306406157")  # True, auto-detects the format from length
```

Note that ISBN-13s starting with `979` (a range assigned after the ISBN-10
space filled up) have no ISBN-10 equivalent; converting one raises
`ValueError`.

ISBN-13's check digit is really just the EAN-13 barcode algorithm, and
UPC-A uses the same algorithm one digit shorter (pad an 11-digit UPC-A
payload with a leading 0 and it lines up with EAN-13's weights). Those are
exposed directly for barcode use outside of books:

```python
from isbnconv import ean13_check_digit, is_valid_ean13, is_valid_upca, upca_check_digit

ean13_check_digit("400638133393")  # "1"
is_valid_ean13("4006381333931")    # True
upca_check_digit("03600029145")    # "2"
is_valid_upca("036000291452")      # True
```

## Install

No dependencies beyond the standard library.

```
pip install -e .
```

or just run it in place with `python -m isbnconv`.

## Testing

```
pip install -e ".[test]"
pytest
```
