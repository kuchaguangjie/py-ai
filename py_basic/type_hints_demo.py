"""
type_hints_demo.py
==================

A hands-on tour of the **modern Python type system** (Python 3.12+ / PEP 695).
Each section below is self-contained and ends with runnable output, so the file
doubles as documentation and as an executable demo.

这是一份 Python 3.12+ 现代类型系统的动手演示。每个小节相互独立，
并且都配有可运行的输出，因此本文件既是文档，也是可直接执行的示例。

Topics covered / 涵盖主题
-------------------------
1. Native generics           原生泛型语法      ``class Stack[T]`` / ``def fn[T]()``
2. Protocols                 结构化子类型      ``Protocol`` (Go-style interfaces)
3. Type guards               类型守卫          ``TypeIs`` (Python 3.13)
4. Modern unions & aliases   联合类型与别名    ``X | Y`` / ``type Alias = ...``

Exposes / 对外接口::

    demo() -> None    # print all four examples; registered in main.py

Run it directly / 直接运行::

    uv run python -m py_basic.type_hints_demo   # recommended
    uv run python main.py type-hints            # via the dispatcher
    make demo                                   # via Makefile
"""

from collections.abc import Sequence
from typing import Protocol, TypeIs

# ===========================================================================
# 1. Modern generic syntax — Python 3.12+ (PEP 695)
#    现代泛型语法：无需再导入 TypeVar / Generic，直接用 [T] 声明类型参数。
# ===========================================================================


class Stack[T]:
    """A minimal LIFO stack that is generic over its element type ``T``.

    一个基于 ``list`` 的最小后进先出（LIFO）栈，其元素类型 ``T`` 由调用方指定，
    例如 ``Stack[int]``、``Stack[str]``。
    """

    def __init__(self) -> None:
        # ``list[T]`` is only a static annotation; at runtime it is a plain list.
        # ``list[T]`` 只是静态标注，运行时仍是普通 list。
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Push ``item`` onto the top of the stack. / 将元素压入栈顶。"""
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return the top item.

        Raises:
            IndexError: if the stack is empty.

        弹出并返回栈顶元素；若栈为空则抛出 ``IndexError``。
        """
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def is_empty(self) -> bool:
        """Return ``True`` when the stack holds no items. / 栈为空时返回 True。"""
        return len(self._items) == 0

    def __repr__(self) -> str:
        # Debug-friendly representation, e.g. ``Stack([1, 2, 3])``.
        return f"Stack({self._items})"


# Generic function with a *type constraint* (PEP 695).
# ``[T: (int, float)]`` limits ``T`` to ``int`` or ``float`` only.
# 带类型约束的泛型函数：T 只能是 int 或 float。
def double_values[T: (int, float)](items: Sequence[T]) -> list[T]:
    """Return a new list with every value doubled. / 返回元素全部翻倍的新列表。"""
    return [item * 2 for item in items]


# ===========================================================================
# 2. Protocol — structural typing (duck typing, checked statically)
#    Protocol：结构化子类型（"鸭子类型"）。只要对象实现了对应方法，
#    就自动符合该协议，无需显式继承。
# ===========================================================================


class Renderable(Protocol):
    """Anything that can render itself to a string.

    任何能够把自身渲染为字符串的类型都满足此协议。
    """

    def render(self) -> str: ...


class UserProfile:
    """Does **not** declare inheritance from ``Renderable`` — yet it matches.

    本类并未声明继承 ``Renderable``，但因为实现了 ``render``，
    所以仍然满足该协议。
    """

    def __init__(self, username: str) -> None:
        self.username = username

    def render(self) -> str:
        return f"<UserCard: {self.username}>"


class OrderItem:
    """Another unrelated class that happens to implement ``render``.

    另一个与 UserProfile 无任何继承关系的类，同样实现了 ``render``。
    """

    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price

    def render(self) -> str:
        return f"<Item: {self.name} - ${self.price:.2f}>"


def display_component(component: Renderable) -> None:
    """Accept anything satisfying the ``Renderable`` protocol.

    接受任何符合 ``Renderable`` 协议的对象，调用其 ``render`` 方法。
    """
    print(f"[Render Engine] {component.render()}")


# ===========================================================================
# 3. TypeGuard / TypeIs — runtime type narrowing
#    类型守卫：类似 TypeScript 的 ``is`` 关键字，配合类型检查器做类型窄化。
#    ``TypeIs`` (Python 3.13) narrows in *both* the True and False branches.
# ===========================================================================


class AdminUser:
    def __init__(self, name: str, permissions: list[str]) -> None:
        self.name = name
        self.permissions = permissions


class GuestUser:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id


# PEP 695 type-alias statement — replaces ``Union[AdminUser, GuestUser]``.
# PEP 695 类型别名语法，取代传统的 Union[...]。
type User = AdminUser | GuestUser


def is_admin(user: User) -> TypeIs[AdminUser]:
    """Narrow ``User`` to ``AdminUser`` when it is an admin.

    使用 Python 3.13 的原生 ``TypeIs``，实现双向类型窄化：
    返回 True 时收窄为 AdminUser，返回 False 时自动排除 AdminUser。
    """
    return isinstance(user, AdminUser)


def handle_user_login(user: User) -> str:
    """Branch on the concrete user type and build a greeting.

    根据用户的具体类型分支处理并生成欢迎语。
    """
    if is_admin(user):
        # True branch: ``user`` is narrowed to ``AdminUser``.
        # True 分支：user 被窄化为 AdminUser，可安全访问 name / permissions。
        return f"管理员登录: {user.name}, 权限列表: {', '.join(user.permissions)}"
    else:
        # False branch: ``user`` is precisely narrowed to ``GuestUser``.
        # False 分支：user 被精准推断为 GuestUser（已排除 AdminUser）。
        return f"访客登录: Session ID = {user.session_id}"


# ===========================================================================
# 4. Modern unions & type aliases (PEP 604 / PEP 695)
#    现代联合类型与别名：用 ``|`` 取代 Union / Optional。
# ===========================================================================

type Numeric = int | float  # instead of Union[int, float]
type MaybeString = str | None  # instead of Optional[str]


def parse_score(score_str: str) -> MaybeString:
    """Format a numeric string as ``"Score: X"``, or ``None`` when invalid.

    将数字字符串格式化为 ``"Score: X"``；解析失败时返回 ``None``。
    """
    try:
        val = float(score_str)
        return f"Score: {val:.1f}"
    except ValueError:
        return None


# ===========================================================================
# Demo runner — prints the output of every section above.
# 演示运行器：依次打印上面各小节的输出结果。
# ===========================================================================


def demo() -> None:
    """Execute all examples in order and print their results.

    依次运行全部示例并打印结果。这是本模块对外的统一入口（约定名 ``demo``），
    可被 ``main.py`` 的注册表调用。断言式的回归测试见 ``tests/`` 目录。
    """
    print("--- 1. 测试 Python 3.12+ 现代泛型 ---")
    int_stack = Stack[int]()
    int_stack.push(10)
    int_stack.push(20)
    print(f"Int Stack: {int_stack}")
    print(f"Popped: {int_stack.pop()}")

    str_stack = Stack[str]()
    str_stack.push("Hello")
    str_stack.push("Python 3.12")
    print(f"Str Stack: {str_stack}\n")

    print(f"Double values: {double_values([1, 2, 3.5])}\n")

    print("--- 2. 测试 Protocol (Go 风格结构化类型) ---")
    user = UserProfile(username="eric")
    item = OrderItem(name="Mechanical Keyboard", price=129.9)

    # Two objects with no common base class both fit the same parameter.
    # 两个完全没有公共基类的对象，都能传入同一个参数。
    display_component(user)
    display_component(item)
    print()

    print("--- 3. 测试 TypeGuard (类型守卫) ---")
    admin = AdminUser(name="Alice", permissions=["READ", "WRITE", "DELETE"])
    guest = GuestUser(session_id="sess_998234")

    print(handle_user_login(admin))
    print(handle_user_login(guest))
    print()

    print("--- 4. 测试 Modern Union (|) 与 Type Alias ---")
    print(f"Valid score parse: {parse_score('98.5')}")
    print(f"Invalid score parse: {parse_score('invalid')}")


# Allow ``python -m py_basic.type_hints_demo`` to run the demo directly.
# 允许通过 ``python -m py_basic.type_hints_demo`` 直接运行演示。
if __name__ == "__main__":
    demo()
