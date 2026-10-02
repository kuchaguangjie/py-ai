"""
Tests for :mod:`py_basic.type_hints_demo`.

These are real, assertion-based regression tests for the *logic*; the printable
``demo()`` output is covered only by a light smoke test at the bottom.

本文件针对 ``py_basic.type_hints_demo`` 的**逻辑**做断言式回归测试；
可打印的 ``demo()`` 输出只在文件末尾做一次轻量冒烟测试。

Run / 运行::

    uv run pytest            # or: make test
"""

from __future__ import annotations

import pytest

from py_basic.type_hints_demo import (
    AdminUser,
    GuestUser,
    OrderItem,
    Stack,
    UserProfile,
    demo,
    display_component,
    double_values,
    handle_user_login,
    is_admin,
    parse_score,
)


# ---------------------------------------------------------------------------
# 1. Native generics / 原生泛型
# ---------------------------------------------------------------------------
class TestStack:
    def test_push_pop_is_lifo(self) -> None:
        stack: Stack[int] = Stack()
        stack.push(1)
        stack.push(2)
        assert stack.pop() == 2  # last in, first out
        assert stack.pop() == 1

    def test_is_empty(self) -> None:
        stack: Stack[str] = Stack()
        assert stack.is_empty() is True
        stack.push("x")
        assert stack.is_empty() is False

    def test_pop_on_empty_raises(self) -> None:
        with pytest.raises(IndexError):
            Stack[int]().pop()

    def test_repr(self) -> None:
        stack: Stack[int] = Stack()
        stack.push(10)
        stack.push(20)
        assert repr(stack) == "Stack([10, 20])"


def test_double_values_with_mixed_numbers() -> None:
    assert double_values([1, 2, 3.5]) == [2, 4, 7.0]


def test_double_values_with_empty_sequence() -> None:
    assert double_values([]) == []


# ---------------------------------------------------------------------------
# 2. Protocol / 结构化子类型
# ---------------------------------------------------------------------------
def test_render_methods() -> None:
    assert UserProfile("eric").render() == "<UserCard: eric>"
    assert OrderItem("KBD", 10.0).render() == "<Item: KBD - $10.00>"


def test_display_component_accepts_unrelated_types(capsys: pytest.CaptureFixture[str]) -> None:
    # Two classes with no common base class both satisfy ``Renderable``.
    display_component(UserProfile("eric"))
    display_component(OrderItem("KBD", 10.0))
    out = capsys.readouterr().out
    assert "[Render Engine] <UserCard: eric>" in out
    assert "[Render Engine] <Item: KBD - $10.00>" in out


# ---------------------------------------------------------------------------
# 3. TypeIs type guards / 类型守卫
# ---------------------------------------------------------------------------
def test_is_admin_narrows_true_and_false() -> None:
    assert is_admin(AdminUser("Alice", ["READ"])) is True
    assert is_admin(GuestUser("sess_1")) is False


def test_handle_user_login_admin_branch() -> None:
    admin = AdminUser("Alice", ["READ", "WRITE"])
    assert handle_user_login(admin) == "管理员登录: Alice, 权限列表: READ, WRITE"


def test_handle_user_login_guest_branch() -> None:
    guest = GuestUser("sess_998234")
    assert handle_user_login(guest) == "访客登录: Session ID = sess_998234"


# ---------------------------------------------------------------------------
# 4. Modern unions & aliases / 联合类型与别名
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("98.5", "Score: 98.5"),
        ("0", "Score: 0.0"),
        ("-3.25", "Score: -3.2"),  # :.1f rounds to one decimal
        ("invalid", None),
        ("", None),
    ],
)
def test_parse_score(raw: str, expected: str | None) -> None:
    assert parse_score(raw) == expected


# ---------------------------------------------------------------------------
# Smoke test for the printable demo entry point (``demo()``)
# ---------------------------------------------------------------------------
def test_demo_runs_without_error(capsys: pytest.CaptureFixture[str]) -> None:
    demo()
    out = capsys.readouterr().out
    assert "现代泛型" in out
    assert "Int Stack: Stack([10, 20])" in out
    assert "Invalid score parse: None" in out
