"""
main.py
=======

Entry point & **demo dispatcher** for the ``py-ai`` project.

`py-ai` 项目的入口，同时充当演示（demo）分发器。

Rather than hard-coding one script, ``main.py`` keeps a small *registry* that
maps a short name to the ``demo()`` callable of a sub-module. Adding a new topic
is therefore a two-step job:

1. create the module, e.g. ``py_basic/loops_demo.py``, and expose ``demo()``;
2. add one line to :data:`DEMOS` below.

`main.py` 不写死单个脚本，而是维护一张“名称 -> 模块 demo()”的注册表。
新增主题只需两步：写好带 ``demo()`` 的模块，然后在 :data:`DEMOS` 里登记一行。

Usage / 用法::

    uv run python main.py                 # run every registered demo
    uv run python main.py --list          # list demo names
    uv run python main.py type-hints      # run one specific demo
    make run                              # equivalent shortcut
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from py_basic.async_demo import demo as async_demo
from py_basic.type_hints_demo import demo as type_hints_demo

# ---------------------------------------------------------------------------
# Demo registry  ——  name -> (one-line summary, zero-arg callable)
# 演示注册表：名称 -> (一句话说明, 无参可调用对象)
#
# To add a new demo / 新增演示：
#     from py_basic.loops_demo import demo as loops_demo
#     DEMOS["loops"] = ("for / while loops", loops_demo)
# ---------------------------------------------------------------------------
DEMOS: dict[str, tuple[str, Callable[[], None]]] = {
    "type-hints": ("Modern type system, Python 3.12+ / PEP 695", type_hints_demo),
    "async": ("Asyncio concurrency & streaming (async/await, gather, AsyncGenerator)", async_demo),
}

def list_demos() -> None:
    """Print every registered demo name with its summary. / 列出全部演示。"""
    width = max(len(name) for name in DEMOS)
    print("Available demos / 可用演示:")
    for name, (summary, _) in DEMOS.items():
        print(f"  {name:<{width}}  {summary}")


def run_demo(name: str) -> None:
    """Run a single demo by name, printing a header first.

    按名称运行单个演示，并先打印标题。
    """
    summary, fn = DEMOS[name]
    print(f"=== {name} — {summary} ===\n")
    fn()
    print()


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the requested demo(s).

    解析命令行参数，并分发到指定的演示；返回进程退出码。
    """
    parser = argparse.ArgumentParser(
        prog="py-ai",
        description="Run py-ai demo modules / 运行 py-ai 演示模块。",
    )
    parser.add_argument(
        "names",
        nargs="*",
        help="demo name(s) to run; omit to run all / 要运行的演示名，省略则运行全部",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list available demos and exit / 列出全部演示后退出",
    )
    args = parser.parse_args(argv)

    if args.list:
        list_demos()
        return 0

    names = args.names or list(DEMOS)

    unknown = [n for n in names if n not in DEMOS]
    if unknown:
        parser.error(f"unknown demo(s): {', '.join(unknown)} (see --list)")

    for name in names:
        run_demo(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
