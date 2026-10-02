# py-ai（繁體中文）

**語言 / Languages:** [English](../../README.md) | [简体中文](../zh-CN/README.md) | [繁體中文](README.md)

一個可執行的 **Python 現代特性實驗場**：從型別系統（Python 3.12+ / PEP 695）
起步，未來可擴展到 AI 相關主題。

所有範例皆可直接執行，且核心邏輯都有 `pytest` 測試涵蓋，因此本專案既是
文件，也是經過迴歸測試的參考程式碼。

## 內含的示範

| 名稱         | 主題                  | PEP |
|--------------|-----------------------|-----|
| `type-hints` | 原生泛型              | [695](https://peps.python.org/pep-0695/) |
|              | 結構化子型別          | [544](https://peps.python.org/pep-0544/) |
|              | 型別守衛（`TypeIs`）  | [742](https://peps.python.org/pep-0742/) |
|              | 聯合型別與別名        | [604](https://peps.python.org/pep-0604/) / [695](https://peps.python.org/pep-0695/) |

執行 `uv run main.py --list` 可查看目前註冊的全部示範。

## 環境需求

- Python **3.13+**（範例使用了 `TypeIs` 與 `type` 語句）
- [uv](https://docs.astral.sh/uv/) —— 相依套件與虛擬環境管理

## 快速開始

```bash
git clone <your-repo-url> py-ai
cd py-ai

uv sync                      # 建立虛擬環境並安裝開發相依套件（pytest、pyright）
uv run main.py               # 執行全部已註冊的示範
```

## 專案結構

```
py-ai/
├── main.py                 # 入口 + 示範分派器（註冊表模式）
├── py_basic/               # Python 語言基礎主題
│   ├── __init__.py
│   └── type_hints_demo.py  # 4 個小節：泛型、Protocol、TypeIs、聯合型別
├── tests/                  # pytest 迴歸測試
│   ├── test_type_hints_demo.py
│   └── test_main.py        # 針對分派器本身的測試
├── pyproject.toml          # 中介資料 + 開發相依套件 + pytest 設定
├── Makefile                # 開發快捷指令（run / test / check / clean ...）
├── uv.lock                 # 相依套件鎖定檔
└── doc/
    ├── zh-CN/README.md     # 簡體中文文件
    └── zh-TW/README.md     # 繁體中文文件（本檔）
```

`py_ai/` 預留給未來的 AI 主題模組，與 `py_basic/` 對稱。

## 使用方式

`main.py` 是一個小型**分派器**：將簡短名稱對應到各子模組的 `demo()` 函式，
因此新增主題時無需修改命令列邏輯。

```bash
uv run main.py                        # 執行全部已註冊示範
uv run main.py --list                 # 列出示範名稱與說明
uv run main.py type-hints             # 只執行某一個示範
uv run python -m py_basic.type_hints_demo   # 直接執行某個模組
```

等價的 Make 快捷方式：

```bash
make run      # == uv run main.py
make list     # == uv run main.py --list
make demo     # == uv run py_basic/type_hints_demo.py
```

### 新增一個示範

1. 新增模組並匯出一個無參數的 `demo()` 函式：

   ```python
   # py_basic/loops_demo.py
   def demo() -> None:
       print("for / while 迴圈 ...")
   ```

2. 在 `main.py` 中註冊（兩行）：

   ```python
   from py_basic.loops_demo import demo as loops_demo

   DEMOS["loops"] = ("for / while loops", loops_demo)
   ```

完成後 `uv run main.py loops` 與 `uv run main.py --list` 就會自動包含它。

## 測試

示範負責**輸出**，測試負責**斷言**。`tests/` 涵蓋型別提示示範的真實邏輯
（堆疊行為、協定分派、型別守衛分支、分數解析），以及分派器本身；
對可輸出的 `demo()` 僅做一次冒煙測試。

```bash
uv run pytest          # 或：make test
uv run pytest -v       # 詳細輸出
uv run pytest -k parse # 依關鍵字過濾
```

## 型別檢查

```bash
uv run pyright         # 或：make check
```

## Make 指令

執行 `make`（或 `make help`）可列出全部指令，常用如下：

| 指令 | 說明 |
|------|------|
| `make sync` / `make install` | 依 `uv.lock` 建立或更新虛擬環境 |
| `make run`    | 執行全部已註冊示範 |
| `make list`   | 列出已註冊示範 |
| `make demo`   | 直接執行 `py_basic/type_hints_demo.py` |
| `make test`   | 執行 pytest 測試套件 |
| `make check` / `make typecheck` | 使用 `pyright` 做型別檢查 |
| `make clean`  | 刪除 `__pycache__`、`*.pyc`、`.pytest_cache` |
| `make distclean` | 在 `clean` 基礎上再刪除 `.venv` |

## 各小節說明

1. **原生泛型（PEP 695）**：不再需要 `TypeVar` / `Generic`，直接以
   `Stack[T]` 宣告型別參數；`[T: (int, float)]` 還能為型別參數加上限制。
2. **Protocol（PEP 544）**：結構化子型別（「鴨子型別」）。只要實作了
   `render` 方法，就自動符合 `Renderable` 協定，無需明確繼承。
3. **TypeIs 型別守衛（PEP 742）**：Python 3.13 原生支援，可在 `if / else`
   兩個分支上做雙向型別窄化。
4. **聯合型別與別名（PEP 604 / 695）**：以 `int | float` 取代
   `Union[int, float]`，以 `str | None` 取代 `Optional[str]`。

## 參考資料

- [PEP 695 — 型別參數語法](https://peps.python.org/pep-0695/)
- [PEP 544 — 協定與結構化子型別](https://peps.python.org/pep-0544/)
- [PEP 742 — TypeIs](https://peps.python.org/pep-0742/)
- [PEP 604 — 聯合型別語法 `X | Y`](https://peps.python.org/pep-0604/)
- [Python typing 官方文件](https://docs.python.org/3/library/typing.html)

## 授權條款

以 **MIT License** 發布。
