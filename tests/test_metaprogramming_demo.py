"""
tests/test_metaprogramming_demo.py
==================================

Unit tests for py_basic/metaprogramming_demo.py
py_basic/metaprogramming_demo.py 的单元测试。

测试要点：
  - 装饰器属于「元数据」层面的改动，因此断言集中在函数名/文档/签名是否被保留，
    以及类属性、方法是否被真正注入。
  - 校验逻辑（绑定失败、缺 process 方法）应在**调用或装饰期**就抛 TypeError，
    即「快速失败」，用例用 ``pytest.raises`` 覆盖这些异常分支。
  - 所有用例都是同步函数：被测代码本身是同步的，只有最后的 ``demo()``
    冒烟测试需要把 ``time.sleep`` 打桩掉以避免真实等待。
"""

from unittest.mock import patch

import pytest

from py_basic.metaprogramming_demo import (
    PromptAgent,
    audit_execution,
    calculate_embedding,
    demo,
    register_agent,
)


def test_functools_wraps_preserves_metadata() -> None:
    """测试 functools.wraps 是否成功保留了原函数的元数据（函数名、文档）"""
    # 若没有 @wraps，这里会拿到内部包装函数的名字 "wrapper"
    assert calculate_embedding.__name__ == "calculate_embedding"
    # 同理，__doc__ 也会变成 wrapper 的（None），故用 `or ""` 兜底避免类型问题
    assert "计算文本 Embedding" in (calculate_embedding.__doc__ or "")


def test_audit_execution_binds_arguments() -> None:
    """测试 inspect.Signature 在传入非法参数时直接抛出 TypeError"""
    # 在测试内部临时定义一个被装饰函数，避免依赖示例业务函数的具体签名

    @audit_execution(max_timeout=1.0)
    def dummy_func(a: int, b: str = "default") -> str:
        return f"{a}-{b}"

    # 正确参数调用：省略可选参数 b，apply_defaults() 应自动补上 "default"
    assert dummy_func(10) == "10-default"
    # 正确参数调用：关键字传参应被 sig.bind 正常接受
    assert dummy_func(10, b="custom") == "10-custom"

    # 错误参数调用（少传必选参数 a / 传错关键字参数名）
    # 以下两种错误都由 sig.bind() 在**真正执行函数体之前**拦截，属于「调用即失败」
    with pytest.raises(TypeError):
        dummy_func()  # missing required argument 'a'

    with pytest.raises(TypeError):
        dummy_func(10, invalid_kwarg=123)  # unexpected keyword argument


def test_class_decorator_injection() -> None:
    """测试类装饰器是否动态注入了属性和方法"""
    agent = PromptAgent()

    # 验证元数据与类方法注入
    # getattr 而非 agent._agent_alias：显式表达这是运行时动态注入、静态不可知的属性
    assert getattr(agent, "_agent_alias") == "PromptRefiner"
    assert hasattr(agent, "describe")
    # describe() 是闭包，内容由装饰时传入的 alias 与类名共同决定
    assert agent.describe() == "Agent[PromptRefiner] -> Class: PromptAgent"
    # process() 是类中原本就有的实现，顺带验证它与注入的成员共存无冲突
    assert agent.process(" test ") == "[Refined]: test"


def test_class_decorator_validation() -> None:
    """测试类装饰器对缺乏 `process` 方法的类校验机制"""
    # match 使用正则匹配异常消息，锁定「缺 process」这一具体原因
    # 注意 class 定义语句位于 with 块内：装饰器在类创建完成的那一刻就执行了
    with pytest.raises(TypeError, match="必须实现 `process` 方法"):

        @register_agent(alias="InvalidAgent")
        class InvalidClass:
            pass


def test_demo_entrypoint() -> None:
    """测试 demo() 入口正常运行（模拟 sleep 瞬间完成）"""
    # demo() 里唯一的「真实等待」来自 calculate_embedding 的 time.sleep(0.01)，
    # 打桩为立即返回可让冒烟测试保持毫秒级；
    # 用例只关心 demo() 能否跑通（不抛异常、正常打印），因此不断言 WARN 是否出现。
    with patch("time.sleep", return_value=None):
        demo()
