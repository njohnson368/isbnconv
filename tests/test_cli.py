import io

import pytest

from isbnconv import cli


def test_converts_from_file(tmp_path, capsys):
    path = tmp_path / "books.txt"
    path.write_text("0-306-40615-2\n978-0-13-468599-1\n")

    exit_code = cli.main([str(path)])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "0-306-40615-2 -> 9780306406157" in out
    assert "978-0-13-468599-1 -> 0134685997" in out


def test_converts_from_stdin_by_default(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("0306406152\n"))

    exit_code = cli.main([])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.strip() == "0306406152 -> 9780306406157"


def test_explicit_dash_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("0306406152\n"))

    exit_code = cli.main(["-"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.strip() == "0306406152 -> 9780306406157"


def test_skips_blank_lines_and_comments(tmp_path, capsys):
    path = tmp_path / "books.txt"
    path.write_text("# a comment\n\n0306406152\n")

    exit_code = cli.main([str(path)])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.strip() == "0306406152 -> 9780306406157"


def test_invalid_isbn_reported_on_stderr_and_nonzero_exit(tmp_path, capsys):
    path = tmp_path / "books.txt"
    path.write_text("1234567890\n")

    exit_code = cli.main([str(path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "1234567890" in captured.err
    assert "not a valid ISBN-10" in captured.err


def test_batch_continues_after_invalid_entry(tmp_path, capsys):
    path = tmp_path / "books.txt"
    path.write_text("1234567890\n0306406152\n")

    exit_code = cli.main([str(path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "0306406152 -> 9780306406157" in captured.out
    assert "1234567890" in captured.err


def test_multiple_files_are_concatenated(tmp_path, capsys):
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("0306406152\n")
    second.write_text("978-0-306-40615-7\n")

    exit_code = cli.main([str(first), str(second)])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "0306406152 -> 9780306406157" in out
    assert "978-0-306-40615-7 -> 0306406152" in out


class TestValidateOnly:
    def test_reports_valid_and_invalid(self, tmp_path, capsys):
        path = tmp_path / "books.txt"
        path.write_text("0306406152\n1234567890\n")

        exit_code = cli.main(["--validate-only", str(path)])

        out = capsys.readouterr().out
        assert exit_code == 1
        assert "0306406152: valid" in out
        assert "1234567890: invalid" in out

    def test_all_valid_exits_zero(self, tmp_path, capsys):
        path = tmp_path / "books.txt"
        path.write_text("0306406152\n9780306406157\n")

        exit_code = cli.main(["--validate-only", str(path)])

        assert exit_code == 0
