"""Parse and format byte sizes such as ``1.5 MiB`` and ``512``.

Every project that reads a ``--max-size`` flag grows one of these, and the two easy
mistakes are always the same: treating ``MB`` as 1024-based and mixing binary with
decimal suffixes in one table.

    >>> from parse_size import format_size, parse_size
    >>> parse_size("1.5 MB")
    1500000
    >>> parse_size("1.5 MiB")
    1572864
    >>> format_size(1572864, binary=True)
    '1.5 MiB'

Standard library only, Python 3.9+.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

__all__ = ["SizeParseError", "format_size", "parse_size"]

__version__ = "0.1.0"

_DECIMAL_UNITS = {
    "b": 1,
    "k": 1000,
    "kb": 1000,
    "kilobyte": 1000,
    "kilobytes": 1000,
    "m": 1000**2,
    "mb": 1000**2,
    "megabyte": 1000**2,
    "megabytes": 1000**2,
    "g": 1000**3,
    "gb": 1000**3,
    "gigabyte": 1000**3,
    "gigabytes": 1000**3,
    "t": 1000**4,
    "tb": 1000**4,
    "terabyte": 1000**4,
    "terabytes": 1000**4,
    "p": 1000**5,
    "pb": 1000**5,
    "petabyte": 1000**5,
    "petabytes": 1000**5,
}
_BINARY_UNITS = {
    "ki": 1024,
    "kib": 1024,
    "kibibyte": 1024,
    "kibibytes": 1024,
    "mi": 1024**2,
    "mib": 1024**2,
    "mebibyte": 1024**2,
    "mebibytes": 1024**2,
    "gi": 1024**3,
    "gib": 1024**3,
    "gibibyte": 1024**3,
    "gibibytes": 1024**3,
    "ti": 1024**4,
    "tib": 1024**4,
    "tebibyte": 1024**4,
    "tebibytes": 1024**4,
    "pi": 1024**5,
    "pib": 1024**5,
    "pebibyte": 1024**5,
    "pebibytes": 1024**5,
}
_NUMBER = re.compile(r"^(?P<number>[+-]?(?:\d+(?:\.\d+)?|\.\d+))(?P<unit>[A-Za-z]*)$")
_DECIMAL_SUFFIXES = ("B", "KB", "MB", "GB", "TB", "PB")
_BINARY_SUFFIXES = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")


class SizeParseError(ValueError):
    """A value that is not a byte size."""


def parse_size(text: str, *, default_unit: str = "B", allow_negative: bool = False) -> int:
    """Parse ``"512"``, ``"1.5 MB"``, ``"10MiB"`` or ``"2 gigabytes"`` into bytes.

    A bare number is read in ``default_unit``. ``KB`` family suffixes are powers of 1000
    and ``KiB`` family suffixes are powers of 1024, as in the IEC standard. Fractional
    results are rounded half up.
    """
    if not isinstance(text, str):
        raise SizeParseError(f"expected a string, got {type(text).__name__}")
    compact = re.sub(r"[\s_]", "", text)
    if not compact:
        raise SizeParseError("empty size")
    match = _NUMBER.match(compact)
    if not match:
        raise SizeParseError(f"not a size: {text!r}")
    try:
        value = Decimal(match.group("number"))
    except InvalidOperation:  # pragma: no cover - the regex already rejects these
        raise SizeParseError(f"not a number: {text!r}") from None
    if value < 0 and not allow_negative:
        raise SizeParseError(f"negative size: {text!r}")

    unit = match.group("unit").lower()
    if not unit:
        unit = default_unit.lower()
    factor = _DECIMAL_UNITS.get(unit) or _BINARY_UNITS.get(unit)
    if factor is None:
        known = ", ".join(sorted({*_DECIMAL_UNITS, *_BINARY_UNITS}))
        raise SizeParseError(f"unknown unit {match.group('unit')!r}; known: {known}")
    total = (value * factor).to_integral_value(rounding=ROUND_HALF_UP)
    return int(total)


def format_size(
    size: int,
    *,
    binary: bool = False,
    precision: int | None = 1,
    space: bool = True,
) -> str:
    """Format a byte count, choosing the largest unit that keeps it at or above one.

    ``precision`` is the number of decimals (trailing zeros trimmed); ``None`` keeps the
    value exact, which makes ``parse_size(format_size(n)) == n`` hold.
    """
    if isinstance(size, bool) or not isinstance(size, int):
        raise SizeParseError(f"expected an int, got {type(size).__name__}")
    suffixes = _BINARY_SUFFIXES if binary else _DECIMAL_SUFFIXES
    step = 1024 if binary else 1000
    sign = "-" if size < 0 else ""
    magnitude = abs(size)
    index = 0
    while index + 1 < len(suffixes) and magnitude >= step ** (index + 1):
        index += 1
    value = magnitude / (step**index) if index else float(magnitude)
    if precision is None:
        text = f"{value:.12f}".rstrip("0").rstrip(".") if index else str(magnitude)
    else:
        text = f"{value:.{max(precision, 0)}f}"
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if not text:
            text = "0"
    separator = " " if space else ""
    return f"{sign}{text}{separator}{suffixes[index]}"
