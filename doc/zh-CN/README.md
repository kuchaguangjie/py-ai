# py-ai（简体中文）

**语言 / Languages:** [English](../../README.md) | [简体中文](README.md) | [繁體中文](../zh-TW/README.md)

一个可运行的 **Python 现代特性实验场**：从类型系统（Python 3.12+ / PEP 695）
起步，未来可扩展到 AI 相关主题。

所有示例均可直接运行，并且核心逻辑都有 `pytest` 测试覆盖，因此本仓库既是
文档，也是经过回归测试的参考代码。

## 包含的演示

| 名称         | 主题                  | PEP |
|--------------|-----------------------|-----|
| `type-hints` | 原生泛型              | [695](https://peps.python.org/pep-0695/) |
|              | 结构化子类型          | [544](https://peps.python.org/pep-0544/) |
|              | 类型守卫（`TypeIs`）  | [742](https://peps.python.org/pep-0742/) |
|              | 联合类型与别名        | [604](https://peps.python.org/pep-0604/) / [695](https://peps.python.org/pep-0695/) |

执行 `uv run main.py --list` 可查看当前注册的全部演示。

## 环境要求

- Python **3.13+**（示例使用了 `TypeIs` 与 `type` 语句）
- [uv](https://docs.astral.sh/uv/) —— 依赖与虚拟环境管理

## 快速开始

```bash
git clone <your-repo-url> py-ai
cd py-ai

uv sync                      # 创建虚拟环境并安装开发依赖（pytest、pyright）
uv run main.py               # 运行全部已注册的演示
```

## 项目结构

```
py-ai/
├── main.py                 # 入口 + 演示分发器（注册表模式）
├── py_basic/               # Python 语言基础主题
│   ├── __init__.py
│   └── type_hints_demo.py  # 4 个小节：泛型、Protocol、TypeIs、联合类型
├── tests/                  # pytest 回归测试
│   ├── test_type_hints_demo.py
│   └── test_main.py        # 针对分发器本身的测试
├── pyproject.toml          # 元数据 + 开发依赖 + pytest 配置
├── Makefile                # 开发快捷命令（run / test / check / clean ...）
├── uv.lock                 # 依赖锁定文件
└── doc/
    ├── zh-CN/README.md     # 简体中文文档（本文件）
    └── zh-TW/README.md     # 繁体中文文档
```

`py_ai/` 预留给未来的 AI 主题模块，与 `py_basic/` 对称。

## 使用方法

`main.py` 是一个小型**分发器**：把简短名称映射到各子模块的 `demo()` 函数，
因此新增主题时无需修改命令行逻辑。

```bash
uv run main.py                        # 运行全部已注册演示
uv run main.py --list                 # 列出演示名称与说明
uv run main.py type-hints             # 只运行某一个演示
uv run python -m py_basic.type_hints_demo   # 直接运行某个模块
```

等价的 Make 快捷方式：

```bash
make run      # == uv run main.py
make list     # == uv run main.py --list
make demo     # == uv run py_basic/type_hints_demo.py
```

### 新增一个演示

1. 新建模块并导出一个无参的 `demo()` 函数：

   ```python
   # py_basic/loops_demo.py
   def demo() -> None:
       print("for / while 循环 ...")
   ```

2. 在 `main.py` 中登记（两行）：

   ```python
   from py_basic.loops_demo import demo as loops_demo

   DEMOS["loops"] = ("for / while loops", loops_demo)
   ```

完成后 `uv run main.py loops` 与 `uv run main.py --list` 就会自动包含它。

## 测试

演示负责**打印**，测试负责**断言**。`tests/` 覆盖类型提示演示的真实逻辑
（栈行为、协议分发、类型守卫分支、分数解析），以及分发器本身；
对可打印的 `demo()` 只做一次冒烟测试。

```bash
uv run pytest          # 或：make test
uv run pytest -v       # 详细输出
uv run pytest -k parse # 按关键字过滤
```

## 类型检查

```bash
uv run pyright         # 或：make check
```

## Make 命令

执行 `make`（或 `make help`）可列出全部命令，常用如下：

| 命令 | 说明 |
|------|------|
| `make sync` / `make install` | 依据 `uv.lock` 创建或更新虚拟环境 |
| `make run`    | 运行全部已注册演示 |
| `make list`   | 列出已注册演示 |
| `make demo`   | 直接运行 `py_basic/type_hints_demo.py` |
| `make test`   | 运行 pytest 测试套件 |
| `make check` / `make typecheck` | 使用 `pyright` 做类型检查 |
| `make clean`  | 删除 `__pycache__`、`*.pyc`、`.pytest_cache` |
| `make distclean` | 在 `clean` 基础上再删除 `.venv` |

## 各小节说明

1. **原生泛型（PEP 695）**：不再需要 `TypeVar` / `Generic`，直接用
   `Stack[T]` 声明类型参数；`[T: (int, float)]` 还能给类型参数加约束。
2. **Protocol（PEP 544）**：结构化子类型（“鸭子类型”）。只要实现了
   `render` 方法，就自动满足 `Renderable` 协议，无需显式继承。
3. **TypeIs 类型守卫（PEP 742）**：Python 3.13 原生支持，可在 `if / else`
   两个分支上做双向类型窄化。
4. **联合类型与别名（PEP 604 / 695）**：用 `int | float` 取代
   `Union[int, float]`，用 `str | None` 取代 `Optional[str]`。

## 参考资料

- [PEP 695 — 类型参数语法](https://peps.python.org/pep-0695/)
- [PEP 544 — 协议与结构化子类型](https://peps.python.org/pep-0544/)
- [PEP 742 — TypeIs](https://peps.python.org/pep-0742/)
- [PEP 604 — 联合类型语法 `X | Y`](https://peps.python.org/pep-0604/)
- [Python typing 官方文档](https://docs.python.org/3/library/typing.html)

## 许可证

基于 **MIT License** 发布。
