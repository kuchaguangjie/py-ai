"""
py_basic/metaprogramming_demo.py
================================

Metaprogramming & Decorators in Python 3.12+
元编程与装饰器示例：
1. functools.wraps & inspect (函数参数分析与类型元数据检查)
2. 自定义参数化函数装饰器 (通用耗时监控与动态校验)
3. 类装饰器 (通过修改/注入元数据增强类属性)

「元编程」= 把函数/类本身当作数据来操作。本模块演示三种常见手法：
  - 运行时读取函数的**签名**（``inspect.signature``），在调用前完成参数校验；
  - 用**装饰器**包装函数，在不改动原函数体的前提下增加横切逻辑（耗时告警）；
  - 用装饰器**修改类的命名空间**（``setattr``）动态注入属性与方法。
"""

from __future__ import annotations  # 让注解延迟求值，可直接书写 dict[str, Any] 等新式语法

from functools import wraps
import inspect
import time
from typing import Any, Callable, TypeVar

# 通用可调用类型变量：``F`` 用于把「装饰器输入/输出的函数类型」绑定在一起，
# 这样包装后的函数在类型检查器眼中仍保持原签名（而非退化成 (*args, **kwargs) -> Any）。
F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# 1. 函数装饰器：基于 inspect 进行动态参数校验与耗时统计
# ---------------------------------------------------------------------------
def audit_execution(max_timeout: float = 1.0) -> Callable[[F], F]:
    """参数化函数装饰器：

    1. 利用 inspect 校验函数参数绑定（确保调用参数符合函数定义）。
    2. 使用 time.perf_counter 记录执行耗时。
    3. 保留原始函数的签名与文档字符串 (functools.wraps)。

    这是「三层结构」（装饰器工厂 -> 装饰器 -> 包装函数）中的**最外层**：
    先接收配置参数（``max_timeout``），再返回真正的装饰器。
    因此使用时必须加括号：``@audit_execution(max_timeout=0.05)``。

    Args:
        max_timeout: 超时告警阈值（秒）。执行耗时超过该值时打印一条 WARN，
            但**不会**中断或抛异常——仅作可观测性提示。

    Returns:
        Callable[[F], F]: 接收函数并返回包装函数的装饰器。
    """

    def decorator(func: F) -> F:
        # 在「装饰时」一次性取出签名对象，避免每次调用都重新解析函数定义（性能考量）
        # 获取函数的形参列表结构（签名对象）
        sig = inspect.signature(func)

        # wraps 会把 func 的 __name__ / __doc__ / __wrapped__ 等元数据复制到 wrapper 上，
        # 让被装饰后的函数「看起来」仍是原函数（调试、日志、IDE 提示都更友好）
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 元编程核心：利用 inspect.Signature 将传入的实参跟形参绑定
            # 如果参数数量或位置不对，在执行前就会抛出 TypeError
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()  # 自动填充缺省默认值

            # perf_counter 是单调高精度时钟，适合测量短间隔耗时（不能用 time.time）
            start = time.perf_counter()
            # 用绑定后的结果回放调用，等价于原样转发 *args / **kwargs
            result = func(*bound_args.args, **bound_args.kwargs)
            elapsed = time.perf_counter() - start

            # 只在超阈值时告警，保持正常路径零噪声
            if elapsed > max_timeout:
                print(
                    f"⚠️ [WARN] 函数 '{func.__name__}' 执行超时! "
                    f"耗时: {elapsed:.4f}s > 阈值: {max_timeout}s"
                )

            return result

        # wrapper 的实际类型是 Callable[..., Any]，而声明要求返回 F；
        # 这正是装饰器模式固有的类型信息丢失，故此处显式忽略该检查。
        return wrapper  # type: ignore[return-value]

    return decorator


# ---------------------------------------------------------------------------
# 2. 类装饰器：拦截和增强类的行为
# ---------------------------------------------------------------------------
def register_agent(alias: str) -> Callable[[type], type]:
    """类装饰器：为 Agent 类自动注入元数据属性和统一方法。

    同样是参数化装饰器：``alias`` 决定注入的别名，
    返回的 ``cls_decorator`` 接收类对象、就地修改后原样返回（也可返回新类）。

    Args:
        alias: 注册别名，会写成类属性 ``_agent_alias``，并被 ``describe()`` 引用。

    Returns:
        Callable[[type], type]: 接收类并返回（增强后的）同一个类的装饰器。

    Raises:
        TypeError: 被装饰的类未定义 ``process`` 方法时抛出（注册期即失败）。
    """

    def cls_decorator(cls: type) -> type:
        # 1. 动态注入类级别的元数据
        #    类装饰器发生在类对象创建之后，所以直接 setattr 就能改「类属性」
        setattr(cls, "_agent_alias", alias)
        setattr(cls, "_registered_at", time.time())

        # 2. 利用 inspect 检查类中是否定义了 process 方法
        #    getmembers 会递归收集继承来的成员，因此子类沿用父类实现也算通过
        members = dict(inspect.getmembers(cls))
        if "process" not in members:
            raise TypeError(f"类 {cls.__name__} 必须实现 `process` 方法才能注册为 Agent")

        # 3. 给该类动态挂载一个通用的身份检查工具函数
        #    闭包捕获了外层的 alias 与 cls，因此每个类的 describe() 各自记住自己的身份
        def describe(self: Any) -> str:
            return f"Agent[{alias}] -> Class: {cls.__name__}"

        # 挂到类上即成为实例方法（self 由 Python 在调用时自动传入）
        setattr(cls, "describe", describe)

        # 原样返回同一个类；装饰器也可以在此 `return type(cls.__name__, ...)` 造一个新类
        return cls

    return cls_decorator


# ---------------------------------------------------------------------------
# 3. 示例业务逻辑
# ---------------------------------------------------------------------------
# max_timeout 设为 0.05s，比该函数真实耗时（约 0.01s）留出余量，故默认不会告警；
# 想观察 WARN 输出可把它调到 0.001 之类更小的值
@audit_execution(max_timeout=0.05)
def calculate_embedding(text: str, model_version: int = 1) -> dict[str, Any]:
    """计算文本 Embedding（模拟延迟）。

    Args:
        text: 待向量化的原始文本。
        model_version: 模型版本号，仅随结果原样返回以便断言。

    Returns:
        dict[str, Any]: 含 ``text`` / ``dim`` / ``version`` 三个键的模拟向量元信息。
    """
    # 模拟一定计算耗时（真实场景此处为模型推理或远程 API 调用）
    time.sleep(0.01)
    return {
        "text": text,
        "dim": 1536,  # 模拟的向量维度
        "version": model_version,
    }


# 该装饰器在「类定义完成时」立即执行：注入 _agent_alias="_agent_alias" 并挂载 describe()
@register_agent(alias="PromptRefiner")
class PromptAgent:
    """提示词优化 Agent 类。"""

    def process(self, prompt: str) -> str:
        """清理首尾空白并加上处理标记（类装饰器校验的就是这个方法的存在）。"""
        return f"[Refined]: {prompt.strip()}"


def demo() -> None:
    """注册表接入入口点：展现元编程与装饰器效果。"""
    print("--- 1. 函数装饰器 & inspect 检查 ---")
    # 装饰后的 calculate_embedding 内部仍会走一遍签名绑定与计时逻辑；
    # 实际耗时约 0.01s，未超过 0.05s 阈值，所以正常情况下看不到 WARN
    # （把阈值调小即可触发告警，例如 audit_execution(max_timeout=0.001)）
    res = calculate_embedding("Hello Python Metaprogramming", model_version=2)
    print(f"Embedding 结果: {res}")
    # wraps 生效的证据：函数名没有被替换成 "wrapper"
    print(f"保留的原始函数名: {calculate_embedding.__name__}")
    # 签名同样被保留：仍显示 (text, model_version=1) 而非 (*args, **kwargs)
    print(f"inspect 获取装饰后函数的真实签名: {inspect.signature(calculate_embedding)}\n")

    print("--- 2. 类装饰器动态注入 ---")
    agent = PromptAgent()
    # 属性并非定义在类体里，而是由 register_agent 在装饰期 setattr 注入
    print(f"动态属性 _agent_alias: {getattr(agent, '_agent_alias')}")
    print(f"动态注入的方法 describe(): {agent.describe()}")
    print(f"执行逻辑 process(): {agent.process('  improve code quality  ')}")


if __name__ == "__main__":
    demo()
