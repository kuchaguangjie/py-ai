"""
Tests for the ``main.py`` demo dispatcher.

针对 ``main.py`` 演示分发器的测试：验证列举、单跑、全跑以及未知名称的处理。

Run / 运行::

    uv run pytest            # or: make test
"""

from __future__ import annotations

import pytest

from main import DEMOS, main


def test_list_demos(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--list"]) == 0
    out = capsys.readouterr().out
    for name in DEMOS:
        assert name in out


def test_run_single_demo(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["type-hints"]) == 0
    assert "type-hints" in capsys.readouterr().out


def test_run_all_demos(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert all(name in out for name in DEMOS)


def test_unknown_demo_exits_with_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["does-not-exist"])
    assert excinfo.value.code == 2  # argparse error exit code
    assert "unknown demo" in capsys.readouterr().err
