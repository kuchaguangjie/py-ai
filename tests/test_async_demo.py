"""
tests/test_async_demo.py
========================

Unit tests for py_basic/async_demo.py
py_basic/async_demo.py 的单元测试。

测试要点：
  - 通过 autouse fixture 把 asyncio.sleep 替换成「零延迟」的 AsyncMock，
    避免真实等待，让整个测试套件瞬间跑完。
  - 用 pytest.mark.asyncio 标记协程测试用例，由 pytest-asyncio 插件驱动事件循环。
  - 覆盖正常路径（请求、并发、流式）以及同步入口 demo() 的可执行性。
"""

from unittest.mock import AsyncMock, patch

import pytest

from py_basic.async_demo import (
    AIStreamer,
    demo,
    fetch_all_models_concurrently,
    simulate_llm_request,
)


# 核心提速魔法：自动拦截该测试文件里所有的 asyncio.sleep，将其替换为 0 秒立刻返回
# autouse=True 表示无需显式声明，本文件内每个测试用例都会自动套用这个 fixture。
@pytest.fixture(autouse=True)
def fast_asyncio_sleep():
    """将 asyncio.sleep 打桩为零延迟协程，消除测试中的真实等待。

    AsyncMock 让被替换的 sleep 依然「可 await」，
    因此被测代码里的 ``await asyncio.sleep(delay)`` 语法不受影响，
    只是会立即返回 None。
    """
    # with 块保证测试结束后 patch 自动撤销，恢复真实的 asyncio.sleep
    with patch("asyncio.sleep", new_callable=AsyncMock):
        yield


@pytest.mark.asyncio
async def test_simulate_llm_request() -> None:
    """单次模拟请求应返回带正确来源与内容的 FetchResult。"""
    res = await simulate_llm_request("TestModel", "Test Prompt", delay=0.01)
    # 来源字段应原样回传传入的模型名
    assert res.source == "TestModel"
    # 内容中应包含原始 prompt（验证 prompt 被正确拼接进回答）
    assert "Test Prompt" in res.content


@pytest.mark.asyncio
async def test_fetch_all_models_concurrently() -> None:
    """并发请求应聚合三个模型的结果。"""
    results = await fetch_all_models_concurrently("Test Prompt")
    # 硬编码了三个模型，因此结果数量固定为 3
    assert len(results) == 3


@pytest.mark.asyncio
async def test_ai_streamer() -> None:
    """异步生成器应逐个产出全部 token，且以结束标记收尾。"""
    streamer = AIStreamer(model_name="TestStreamer")
    # 用异步推导式把整个异步生成器消费成列表，便于断言
    tokens = [t async for t in streamer.stream_tokens("Test")]
    # 与 AIStreamer.stream_tokens 中定义的 token 数量保持一致
    assert len(tokens) == 5
    # 最后一个 token 应为完成标记
    assert tokens[-1] == " (完成)"


def test_demo_entrypoint() -> None:
    """测试同步 demo() 入口正常执行不报错。

    这是个同步用例：demo() 内部通过 asyncio.run 自建事件循环，
    所以这里不需要 pytest.mark.asyncio，也不需要 await。
    """
    demo()
