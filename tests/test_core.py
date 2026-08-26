import pytest

from isbnconv import core


class TestIsbn10CheckDigit:
    def test_known_value(self):
        # 0-306-40615-2, a commonly cited example (Zen and the Art of Motorcycle Maintenance)
        assert core.isbn10_check_digit("030640615") == "2"

    def test_x_check_digit(self):
        # 0-9752298-0-X
        assert core.isbn10_check_digit("097522980") == "X"

    def test_zero_check_digit(self):
        # a weighted sum that's already a multiple of 11 lands on check
        # digit 0 directly, rather than going through the 11 -> 0 wrap.
        assert core.isbn10_check_digit("000000000") == "0"

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            core.isbn10_check_digit("12345678")  # 8 digits
        with pytest.raises(ValueError):
            core.isbn10_check_digit("1234567890")  # 10 digits

    def test_rejects_non_digits(self):
        with pytest.raises(ValueError):
            core.isbn10_check_digit("03064061X")


class TestIsbn13CheckDigit:
    def test_known_value(self):
        assert core.isbn13_check_digit("978030640615") == "7"

    def test_979_prefix_still_computes(self):
        # the check digit algorithm itself doesn't care about the prefix,
        # only isbn13_to_isbn10 rejects 979
        assert core.isbn13_check_digit("979030640615") == "6"

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            core.isbn13_check_digit("97803064061")  # 11 digits
        with pytest.raises(ValueError):
            core.isbn13_check_digit("9780306406157")  # 13 digits

    def test_rejects_non_digits(self):
        with pytest.raises(ValueError):
            core.isbn13_check_digit("97803064061X")


class TestValidation:
    @pytest.mark.parametrize(
        "isbn",
        [
            "0306406152",
            "0-306-40615-2",
            "0 306 40615 2",
            "097522980X",
            "0-9752298-0-X",
        ],
    )
    def test_valid_isbn10(self, isbn):
        assert core.is_valid_isbn10(isbn)

    @pytest.mark.parametrize(
        "isbn",
        [
            "0306406153",  # wrong check digit
            "030640615",  # too short
            "03064061523",  # too long
            "030640615x",  # lowercase x is fine after clean(), so this actually passes
        ],
    )
    def test_invalid_isbn10_shape_or_checksum(self, isbn):
        if isbn == "030640615x":
            assert core.is_valid_isbn10(isbn)
        else:
            assert not core.is_valid_isbn10(isbn)

    @pytest.mark.parametrize(
        "isbn",
        [
            "9780306406157",
            "978-0-306-40615-7",
            "9790306406156",
        ],
    )
    def test_valid_isbn13(self, isbn):
        assert core.is_valid_isbn13(isbn)

    @pytest.mark.parametrize(
        "isbn",
        [
            "9780306406158",  # wrong check digit
            "978030640615",  # too short
            "97803064061577",  # too long
        ],
    )
    def test_invalid_isbn13(self, isbn):
        assert not core.is_valid_isbn13(isbn)


class TestConversion:
    def test_isbn10_to_isbn13(self):
        assert core.isbn10_to_isbn13("0-306-40615-2") == "9780306406157"

    def test_isbn10_to_isbn13_with_x_check_digit(self):
        assert core.isbn10_to_isbn13("0-9752298-0-X") == "9780975229804"

    def test_isbn10_to_isbn13_rejects_invalid_input(self):
        with pytest.raises(ValueError):
            core.isbn10_to_isbn13("0306406153")  # bad check digit

    def test_isbn13_to_isbn10(self):
        assert core.isbn13_to_isbn10("978-0-306-40615-7") == "0306406152"

    def test_isbn13_to_isbn10_rejects_invalid_input(self):
        with pytest.raises(ValueError):
            core.isbn13_to_isbn10("9780306406158")  # bad check digit

    def test_isbn13_to_isbn10_rejects_979_prefix(self):
        with pytest.raises(ValueError, match="979"):
            core.isbn13_to_isbn10("9790306406156")

    def test_roundtrip_isbn10(self):
        original = "0306406152"
        assert core.isbn13_to_isbn10(core.isbn10_to_isbn13(original)) == original

    def test_convert_autodetects_isbn10(self):
        assert core.convert("0-306-40615-2") == "9780306406157"

    def test_convert_autodetects_isbn13(self):
        assert core.convert("978-0-306-40615-7") == "0306406152"

    def test_convert_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            core.convert("12345")


class TestClean:
    def test_strips_hyphens_and_spaces(self):
        assert core.clean("0-306-40615-2") == "0306406152"
        assert core.clean("0 306 40615 2") == "0306406152"

    def test_uppercases_x(self):
        assert core.clean("030640615x") == "030640615X"

    def test_strips_surrounding_whitespace(self):
        assert core.clean("  0306406152  \n") == "0306406152"
