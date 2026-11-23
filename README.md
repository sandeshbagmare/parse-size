<p align="center">
  <img src="https://raw.githubusercontent.com/sandeshbagmare/parse-size/main/assets/banner.svg" width="100%" alt="parse-size: byte sizes in and out, MB and MiB never confused">
</p>

<p align="center">
  <a href="https://pypi.org/project/parse-size/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/parse-size.svg"></a>
  <a href="https://pypi.org/project/parse-size/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/parse-size.svg"></a>
  <a href="https://pypi.org/project/parse-size/"><img alt="Downloads" src="https://img.shields.io/pypi/dm/parse-size.svg"></a>
  <a href="https://github.com/sandeshbagmare/parse-size/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/sandeshbagmare/parse-size/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/sandeshbagmare/parse-size/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/parse-size.svg"></a>
  <a href="https://sandeshbagmare.github.io/parse-size/"><img alt="docs" src="https://img.shields.io/badge/docs-online-2ea44f.svg"></a>
  <a href="https://pypi.org/project/parse-size/"><img alt="zero dependencies" src="https://img.shields.io/badge/dependencies-0-2ea44f.svg"></a>
</p>

<h3 align="center">byte sizes in and out, MB and MiB never confused</h3>
<p align="center"><em>Standard library only. No runtime dependencies. Python 3.9+.</em></p>

<p align="center">
  <img src="https://raw.githubusercontent.com/sandeshbagmare/parse-size/main/assets/how.svg" width="720" alt="how parse-size fits in">
</p>

## Install

```console
pip install parse-size
```

## Use

```python
from parse_size import SizeParseError, format_size, parse_size

parse_size("10 MB")                    # 10_000_000
parse_size("10MiB")                    # 10_485_760
parse_size("2 gigabytes")              # 2_000_000_000
parse_size("5", default_unit="MiB")    # 5_242_880
parse_size("-1 MB", allow_negative=True)

format_size(1_500_000)                       # '1.5 MB'
format_size(1_234_567, precision=0)          # '1 MB'  (rounded, not truncated)
format_size(1_500_000, space=False)          # '1.5MB'
format_size(1_234_567, precision=None)       # '1.234567 MB'  (exact)
format_size(3 * 1024**3, binary=True)        # '3 GiB'
```

A common argparse pair:

```python
parser.add_argument("--max-size", type=parse_size, default="10 MB")
parser.add_argument("--pretty", action="store_true")
# --max-size 1.5GiB  →  1610612736
```

## Rules

| suffix | factor | | suffix | factor |
| ------ | ------ | - | ------ | ------ |
| `B` | 1 | | `KiB` | 1024 |
| `KB` | 1000 | | `MiB` | 1024² |
| `MB` | 1000² | | `GiB` | 1024³ |
| `GB` | 1000³ | | `TiB` | 1024⁴ |
| `TB` | 1000⁴ | | `PiB` | 1024⁵ |
| `PB` | 1000⁵ | | | |

- single-letter aliases (`K`, `M`, `G`, `T`, `P`) are decimal, as in `dd` and `ls -h`
- long names work in singular or plural (`megabyte`, `megabytes`, `mebibytes`)
- case does not matter, whitespace and underscores inside the value do not matter
- fractions round half up to whole bytes, so `0.0005 kB` is 1 byte
- a bare number is read in `default_unit` (`B` unless you say otherwise)
- negative values raise unless `allow_negative=True`

## Limits

- No `%` of a total, no ranges and no "as much as fits" — just one value.
- `format_size` tops out at petabytes; larger values keep growing in `PB`.
- Human-readable output follows IEC suffixes only, never `K`/`M` shorthand.

## Development

```console
python -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/pytest
```

The suite covers every line of the package (`pytest --cov --cov-branch`), and the
examples in the docstrings run as tests through `--doctest-modules`.

## License

MIT.
