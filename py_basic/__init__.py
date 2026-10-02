"""
py_basic
========

Core Python-language learning modules (as opposed to, say, AI/ML topics which
would live in a sibling package such as ``py_ai``).

Each module in this package is expected to expose a zero-argument callable
named ``demo()`` that prints a runnable, self-contained example. ``main.py``
discovers and invokes these through its demo registry.

本包存放 Python 语言基础相关的学习模块（未来 AI/ML 等主题可放在同级的
``py_ai`` 包中）。约定：每个模块导出一个无参函数 ``demo()``，用于打印可运行的
示例；``main.py`` 通过注册表统一调用。

Note / 注意：这里刻意**不**提前导入子模块，避免 ``python -m`` 运行时产生
``RuntimeWarning``；需要时由 ``main.py`` 或测试直接 ``from py_basic.x import ...``。
"""

__all__: list[str] = []
