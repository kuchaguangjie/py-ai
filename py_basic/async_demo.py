"""
py_basic/async_demo.py
======================

Modern async programming in Python 3.12+ (async/await, asyncio.gather, AsyncGenerator).
Python 3.12+ 现代异步编程（async/await、asyncio.gather、异步生成器/流式输出）。

本模块演示了三个核心异步模式：
  1. 单个协程（coroutine）中发起可等待的 I/O 操作（asyncio.sleep）。
  2. 用 asyncio.gather 并发调度多个协程，总耗时约等于最慢的那个任务。
  3. 用异步生成器（async generator）逐块产出数据，模拟 LLM 的流式 Token 输出。
"""

from __future__ import annotations  # 允许在注解中直接使用新式语法（如 list[FetchResult]、str | None）

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResult:
    """一次模拟请求的结果快照（定义为不可变对象，避免被下游意外修改）。

    Attributes:
        source:  数据来源标识，这里用作模型名（如 "Fast-LLM"）。
        content: 模型返回的文本内容。
        elapsed: 该次请求实际等待的秒数。
    """

    source: str
    content: str
    elapsed: float


async def simulate_llm_request(model_name: str, prompt: str, delay: float) -> FetchResult:
    """模拟异步调用 LLM API（用 sleep 代替真实的网络 I/O）。

    由于函数体里有 ``await``，调用它只会返回一个协程对象，
    必须被事件循环调度（await / gather / create_task）才会真正执行。

    Args:
        model_name: 模型名称，同时也作为结果中的来源标识。
        prompt:     发给模型的提示词。
        delay:      模拟的网络延迟秒数；延迟越大代表模型越慢。

    Returns:
        FetchResult: 包含来源、内容和本次实际耗时的结果对象。
    """
    # 用运行中的事件循环计时，比 time.time() 更适合异步场景（单调时钟，不受系统时间调整影响）
    loop = asyncio.get_running_loop()
    start_time = loop.time()

    # 关键：await 会把控制权交还给事件循环，让其他任务在此期间得以执行
    await asyncio.sleep(delay)

    # 保留两位小数，便于打印对照
    elapsed = round(loop.time() - start_time, 2)
    return FetchResult(
        source=model_name,
        content=f"模型 [{model_name}] 针对 '{prompt}' 的回答",
        elapsed=elapsed,
    )


async def fetch_all_models_concurrently(prompt: str) -> list[FetchResult]:
    """并发请求多个模型，演示 asyncio.gather 的用法。

    gather 会一次性把所有协程注册到事件循环上并发执行，
    因此总耗时不等于各任务耗时之和，而是约等于其中最长的一个（1.0s），
    返回结果的顺序与传入参数的顺序严格一致。

    Args:
        prompt: 统一发给所有模型的提示词。

    Returns:
        list[FetchResult]: 按传入顺序排列的模型结果列表。
    """
    results = await asyncio.gather(
        # 三个不同「速度」的模型，故意设置不同 delay 以体现并发效果
        simulate_llm_request("Fast-LLM", prompt, delay=0.3),
        simulate_llm_request("Standard-LLM", prompt, delay=0.5),
        simulate_llm_request("Reasoning-LLM", prompt, delay=1.0),
    )
    # gather 返回的是 tuple，这里转成 list 以便调用方按索引/切片操作
    return list(results)


class AIStreamer:
    """流式 Token 输出器（模拟 LLM 的 Server-Sent Events / 逐字上屏效果）。"""

    def __init__(self, model_name: str) -> None:
        # 记录模型名，用于给每个 token 加前缀
        self.model_name = model_name

    async def stream_tokens(self, prompt: str) -> AsyncGenerator[str]:
        """异步生成器：逐个 ``yield`` token，调用方用 ``async for`` 消费。

        与普通生成器的区别在于函数体内可以 ``await``，
        所以每产出两个 token 之间都能让出控制权（不阻塞事件循环）。

        Args:
            prompt: 提示词（此处仅用于示意，未参与内容生成）。

        Yields:
            str: 单个输出 token。
        """
        # 模拟一段模型输出的 token 序列
        tokens = [f"[{self.model_name}]", " 思考中...", " 答案是:", " 42", " (完成)"]
        for token in tokens:
            # 每产出 token 前先「等待」一下，模拟推理/网络传输的间隔
            await asyncio.sleep(0.12)
            yield token


async def run_async_demos() -> None:
    """核心逻辑主协程：依次演示并发请求与流式输出两块能力。"""
    print("--- 1. asyncio.gather (并发请求多模型) ---")
    loop = asyncio.get_running_loop()
    start = loop.time()  # 记录并发阶段的起始时间，用于验证「总耗时 ≈ 最慢任务」
    results = await fetch_all_models_concurrently(prompt="什么是量子计算？")
    total_elapsed = round(loop.time() - start, 2)

    # 打印各模型的返回结果（:<13 左对齐占位 13 字符，让输出列对齐）
    for res in results:
        print(f"收到回复 -> 源: {res.source:<13} | 耗时: {res.elapsed}s | 内容: {res.content}")
    print(f"并发完成，总耗时: {total_elapsed}s (并行等待最长任务)\n")

    print("--- 2. AsyncGenerator (模拟打字机 Token 流式输出) ---")
    streamer = AIStreamer(model_name="DeepSeek-R1")
    # end="" + flush=True：不换行且立即刷新缓冲区，实现「边生成边显示」的打字机效果
    print("流式输出中: ", end="", flush=True)
    async for token in streamer.stream_tokens(prompt="生命与宇宙的答案"):
        print(token, end="", flush=True)
    print()  # 收尾换行


def demo() -> None:
    """注册表接入入口点：同步包裹启动事件循环。

    ``asyncio.run`` 负责创建事件循环、运行主协程，并在结束后关闭循环。
    因此该函数本身是同步的，可以被普通同步代码（如项目的 demo 注册表）直接调用。
    """
    asyncio.run(run_async_demos())


if __name__ == "__main__":
    demo()
