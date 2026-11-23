"""Tests for parse_size."""

import pytest

from parse_size import SizeParseError, format_size, parse_size


class TestParse:
    def test_a_bare_number_is_bytes(self):
        assert parse_size("512") == 512

    def test_zero(self):
        assert parse_size("0") == 0

    def test_decimal_suffixes_are_powers_of_a_thousand(self):
        assert parse_size("1 KB") == 1000
        assert parse_size("1MB") == 1_000_000
        assert parse_size("2 GB") == 2_000_000_000

    def test_binary_suffixes_are_powers_of_1024(self):
        assert parse_size("1 KiB") == 1024
        assert parse_size("1MiB") == 1024**2
        assert parse_size("4 GiB") == 4 * 1024**3

    def test_a_fraction(self):
        assert parse_size("1.5 MB") == 1_500_000
        assert parse_size("1.5 MiB") == 1_572_864
        assert parse_size(".5 kB") == 500

    def test_rounding_is_half_up(self):
        assert parse_size("0.0005 kB") == 1
        assert parse_size("0.4999 B") == 0

    def test_case_does_not_matter(self):
        assert parse_size("10 mb") == parse_size("10 MB") == parse_size("10Mb")

    def test_long_unit_names(self):
        assert parse_size("2 megabytes") == 2_000_000
        assert parse_size("2 mebibytes") == 2 * 1024**2

    def test_whitespace_and_underscores_are_ignored(self):
        assert parse_size(" 1_000 ") == 1000
        assert parse_size("1. 5\tGB") == parse_size("1.5 GB")

    def test_terabytes_and_petabytes(self):
        assert parse_size("1 TB") == 1000**4
        assert parse_size("1 PiB") == 1024**5

    def test_the_default_unit_can_change(self):
        assert parse_size("5", default_unit="MiB") == 5 * 1024**2

    def test_an_unknown_default_unit_is_reported(self):
        with pytest.raises(SizeParseError, match="unknown unit"):
            parse_size("5", default_unit="furlongs")

    def test_negative_sizes_are_rejected(self):
        with pytest.raises(SizeParseError, match="negative"):
            parse_size("-1 MB")

    def test_negative_sizes_can_be_allowed(self):
        assert parse_size("-1 MB", allow_negative=True) == -1_000_000

    def test_an_unknown_unit(self):
        with pytest.raises(SizeParseError, match="unknown unit 'xz'"):
            parse_size("1 xz")

    def test_text_that_is_not_a_number(self):
        with pytest.raises(SizeParseError, match="not a size"):
            parse_size("big")

    def test_an_empty_value(self):
        with pytest.raises(SizeParseError, match="empty size"):
            parse_size("   ")

    def test_a_non_string(self):
        with pytest.raises(SizeParseError, match="expected a string"):
            parse_size(1024)  # type: ignore[arg-type]

    def test_the_error_is_a_value_error(self):
        assert issubclass(SizeParseError, ValueError)


class TestFormat:
    def test_bytes(self):
        assert format_size(512) == "512 B"

    def test_zero(self):
        assert format_size(0) == "0 B"

    def test_a_thousand(self):
        assert format_size(1000) == "1 KB"

    def test_binary_suffixes(self):
        assert format_size(1024, binary=True) == "1 KiB"
        assert format_size(1536, binary=True) == "1.5 KiB"

    def test_a_fraction_is_rounded_to_the_precision(self):
        assert format_size(1_500_000) == "1.5 MB"
        assert format_size(1_234_567, precision=2) == "1.23 MB"
        assert format_size(1_234_567, precision=0) == "1 MB"

    def test_trailing_zeros_are_trimmed(self):
        assert format_size(2_000_000) == "2 MB"

    def test_the_largest_unit_below_the_value_is_chosen(self):
        assert format_size(999) == "999 B"
        assert format_size(999_999) == "1000 KB"
        assert format_size(1_000_000) == "1 MB"

    def test_no_space(self):
        assert format_size(1_500_000, space=False) == "1.5MB"

    def test_negative_values(self):
        assert format_size(-1_500_000) == "-1.5 MB"

    def test_full_precision_is_exact(self):
        assert format_size(1_234_567, precision=None) == "1.234567 MB"

    def test_a_non_int(self):
        with pytest.raises(SizeParseError, match="expected an int"):
            format_size("1024")  # type: ignore[arg-type]

    def test_a_bool_is_not_a_size(self):
        with pytest.raises(SizeParseError):
            format_size(True)  # type: ignore[arg-type]

    def test_round_trip_at_full_precision(self):
        for size in [0, 1, 512, 999, 1000, 1024, 1_234_567, 5 * 1024**3]:
            assert parse_size(format_size(size, precision=None)) == size
            assert parse_size(format_size(size, binary=True, precision=None)) == size

    def test_round_trip_of_a_formatted_size_keeps_the_value_close(self):
        size = 3 * 1024**3
        assert parse_size(format_size(size, binary=True, precision=1)) == size
