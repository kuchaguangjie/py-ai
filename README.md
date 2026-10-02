# py-ai

**Languages:** [English](README.md) | [简体中文](doc/zh-CN/README.md) | [繁體中文](doc/zh-TW/README.md)

A runnable playground for **modern Python** — starting with the type system
(Python 3.12+ / PEP 695), designed to grow into AI-facing topics.

Every example is executable, and the logic is covered by a `pytest` suite, so
the repo doubles as living documentation and as a regression-tested reference.

[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![Types](https://img.shields.io/badge/typing-pyright-informational.svg)](https://github.com/microsoft/pyright)
[![Tests](https://img.shields.io/badge/tests-pytest-informational.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](#license)

## Demos included

| Name         | Topic                  | PEP |
|--------------|------------------------|-----|
| `type-hints` | Native generics        | [695](https://peps.python.org/pep-0695/) |
|              | Structural typing      | [544](https://peps.python.org/pep-0544/) |
|              | Type guards (`TypeIs`) | [742](https://peps.python.org/pep-0742/) |
|              | Unions & aliases       | [604](https://peps.python.org/pep-0604/) / [695](https://peps.python.org/pep-0695/) |

Run `uv run main.py --list` to see the live list of registered demos.

## Requirements

- Python **3.13+** (the demo uses `TypeIs` and the `type` statement)
- [uv](https://docs.astral.sh/uv/) — dependency & virtualenv management

## Quick start

```bash
git clone <your-repo-url> py-ai
cd py-ai

uv sync                      # create the virtualenv + install dev deps (pytest, pyright)
uv run main.py               # run every registered demo
```

## Project layout

```
py-ai/
├── main.py                 # entry point + demo dispatcher (registry pattern)
├── py_basic/               # Python-language topics
│   ├── __init__.py
│   └── type_hints_demo.py  # 4 sections: generics, Protocol, TypeIs, unions
├── tests/                  # pytest regression tests
│   ├── test_type_hints_demo.py
│   └── test_main.py        # tests for the dispatcher itself
├── pyproject.toml          # metadata + dev deps + pytest config
├── Makefile                # developer shortcuts (run / test / check / clean ...)
├── uv.lock                 # resolved dependency lockfile
└── doc/
    ├── zh-CN/README.md     # Simplified Chinese documentation
    └── zh-TW/README.md     # Traditional Chinese documentation
```

`py_ai/` is reserved for future AI-topic modules, mirroring `py_basic/`.

## Usage

`main.py` is a small **dispatcher**: it maps a short name to each sub-module's
`demo()` function, so you never edit the CLI logic when adding a topic.

```bash
uv run main.py                        # run all registered demos
uv run main.py --list                 # list demo names + summaries
uv run main.py type-hints             # run a single demo
uv run python -m py_basic.type_hints_demo   # run a module directly
```

Equivalent Make shortcuts:

```bash
make run      # == uv run main.py
make list     # == uv run main.py --list
make demo     # == uv run py_basic/type_hints_demo.py
```

### Adding a new demo

1. Create a module exposing a zero-argument `demo()` function:

   ```python
   # py_basic/loops_demo.py
   def demo() -> None:
       print("for / while loops ...")
   ```

2. Register it in `main.py` (two lines):

   ```python
   from py_basic.loops_demo import demo as loops_demo

   DEMOS["loops"] = ("for / while loops", loops_demo)
   ```

That's it — `uv run main.py loops` and `uv run main.py --list` pick it up.

## Testing

Demos *print*; tests *assert*. The `tests/` suite covers the real logic of the
type-hint demo (stack behavior, protocol dispatch, type-guard branches, score
parsing) plus the dispatcher, and only smoke-tests the printable `demo()`.

```bash
uv run pytest          # or: make test
uv run pytest -v       # verbose
uv run pytest -k parse # filter by keyword
```

## Type checking

```bash
uv run pyright         # or: make check
```

## Make targets

Run `make` (or `make help`) to list them all. Most useful:

| Target | Description |
|--------|-------------|
| `make sync` / `make install` | Create or update the virtualenv from `uv.lock` |
| `make run`    | Run every registered demo |
| `make list`   | List registered demos |
| `make demo`   | Run `py_basic/type_hints_demo.py` directly |
| `make test`   | Run the pytest suite |
| `make check` / `make typecheck` | Type-check everything with `pyright` |
| `make clean`  | Delete `__pycache__`, `*.pyc`, `.pytest_cache` |
| `make distclean` | `clean` + remove `.venv` |

## References

- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [PEP 742 — TypeIs](https://peps.python.org/pep-0742/)
- [PEP 604 — Union syntax `X | Y`](https://peps.python.org/pep-0604/)
- [Python typing docs](https://docs.python.org/3/library/typing.html)

## License

Released under the **MIT License** — see LICENSE for details.
