# py-ai

**Languages:** [English](README.md) | [简体中文](doc/zh-CN/README.md) | [繁體中文](doc/zh-TW/README.md)

A runnable playground for **modern Python** — the type system, async
concurrency, and metaprogramming (Python 3.12+ / PEP 695), designed to grow into
AI-facing topics.

Every example is executable, and the logic is covered by a `pytest` suite, so
the repo doubles as living documentation and as a regression-tested reference.

[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![Types](https://img.shields.io/badge/typing-pyright-informational.svg)](https://github.com/microsoft/pyright)
[![Tests](https://img.shields.io/badge/tests-pytest-informational.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](#license)

## Demos included

| Name              | Topic                            | PEP |
|-------------------|----------------------------------|-----|
| `type-hints`      | Native generics                  | [695](https://peps.python.org/pep-0695/) |
|                   | Structural typing                | [544](https://peps.python.org/pep-0544/) |
|                   | Type guards (`TypeIs`)           | [742](https://peps.python.org/pep-0742/) |
|                   | Unions & aliases                 | [604](https://peps.python.org/pep-0604/) / [695](https://peps.python.org/pep-0695/) |
| `async`           | Coroutines (`async` / `await`)   | [492](https://peps.python.org/pep-0492/) |
|                   | Concurrent gathering             | [3156](https://peps.python.org/pep-3156/) |
|                   | Async generators / streaming     | [525](https://peps.python.org/pep-0525/) |
| `metaprogramming` | Function decorators              | [318](https://peps.python.org/pep-0318/) |
|                   | Class decorators & injection     | [3129](https://peps.python.org/pep-3129/) |
|                   | Introspection (`inspect`, `wraps`) | — |

Run `uv run main.py --list` to see the live list of registered demos.

### What each demo covers

**`type-hints`** — the modern type system, in four sections: native generics
(`Stack[T]`, PEP 695), structural typing via `Protocol` (PEP 544), bidirectional
narrowing with `TypeIs` (PEP 742), and union / alias syntax (PEP 604 / 695).

**`async`** — modern async programming: awaiting I/O in a coroutine,
fanning out several "LLM" calls with `asyncio.gather` (total runtime ≈ the
slowest task, not the sum), and streaming tokens from an async generator with
`async for`.

**`metaprogramming`** — treating functions and classes as data: validating
arguments ahead of the call via `inspect.Signature`, wrap-preserving timing
decorators (`functools.wraps`), and a class decorator that injects metadata
attributes and a shared method while rejecting classes without `process()`.

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
│   ├── type_hints_demo.py  # 4 sections: generics, Protocol, TypeIs, unions
│   ├── async_demo.py       # gather / async generators, streaming tokens
│   └── metaprogramming_demo.py  # decorators, inspect, class injection
├── tests/                  # pytest regression tests
│   ├── test_type_hints_demo.py
│   ├── test_async_demo.py
│   ├── test_metaprogramming_demo.py
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
uv run main.py async metaprogramming  # ...or several at once
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

Demos *print*; tests *assert*. The `tests/` suite covers the real logic of every
demo — stack behavior, protocol dispatch, type-guard branches and score parsing
for `type-hints`; request results, gather fan-out and async-generator tokens for
`async`; metadata preservation, argument binding and class injection for
`metaprogramming` — plus the dispatcher itself. Only the printable `demo()`
functions are smoke-tested.

Tests stay fast because the slow paths are stubbed: the async suite patches
`asyncio.sleep` with an `AsyncMock`, and the metaprogramming suite patches
`time.sleep`, so zero real time is spent waiting.

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
- [PEP 492 — `async` / `await` syntax](https://peps.python.org/pep-0492/)
- [PEP 525 — Asynchronous generators](https://peps.python.org/pep-0525/)
- [PEP 318 — Decorators for functions and methods](https://peps.python.org/pep-0318/)
- [PEP 3129 — Class decorators](https://peps.python.org/pep-3129/)
- [Python typing docs](https://docs.python.org/3/library/typing.html)
- [`asyncio` docs](https://docs.python.org/3/library/asyncio.html)
- [`inspect` docs](https://docs.python.org/3/library/inspect.html)

## License

Released under the **MIT License** — see LICENSE for details.
