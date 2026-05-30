"""
进阶 Day 5 演示：错误处理与重试策略

演示三个让系统从"能跑"变成"可靠"的策略：
  1. 重试装饰器（指数退避）
  2. JSON 安全提取 + 降级
  3. 流水线局部失败容忍

运行：
  cd multi_agent
  python adv5_error_handling.py
"""
from __future__ import annotations

import json
import random
import time
from functools import wraps
from typing import Any, Callable, TypeVar

from llm import chat, system, user

F = TypeVar("F", bound=Callable[..., Any])


# ── 策略一：重试装饰器（指数退避）────────────────────────────

def retry(max_attempts: int = 3, base_delay: float = 1.0,
          exceptions: tuple = (Exception,)):
    """
    指数退避重试装饰器。
    第1次失败：等 base_delay 秒，第2次：等 2*base_delay 秒，以此类推。
    只捕获 exceptions 指定的错误类型，不掩盖编程错误。
    """
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_attempts:
                        delay = base_delay * (2 ** (attempt - 1))
                        print(f"  [重试] 第{attempt}次失败：{e}，等 {delay:.1f}s 后重试...")
                        time.sleep(delay)
                    else:
                        print(f"  [重试] 已达最大重试次数（{max_attempts}次），放弃。")
            raise last_error  # type: ignore
        return wrapper  # type: ignore
    return decorator


# 模拟一个不稳定的 API（有概率失败，用于演示重试）
_call_count = 0

def _unstable_api(prompt: str, fail_rate: float = 0.6) -> str:
    global _call_count
    _call_count += 1
    if random.random() < fail_rate:
        raise ConnectionError(f"模拟 API 超时（第 {_call_count} 次调用）")
    return f"成功响应（第 {_call_count} 次）：{prompt[:20]}..."


@retry(max_attempts=3, base_delay=0.3, exceptions=(ConnectionError,))
def call_with_retry(prompt: str) -> str:
    return _unstable_api(prompt, fail_rate=0.6)


def demo_retry() -> None:
    print("=== 演示一：重试装饰器 ===\n")
    random.seed(1)  # seed=1：第1次失败，第2次成功，清晰展示重试过程
    try:
        result = call_with_retry("解释一下什么是机器学习")
        print(f"最终结果：{result}")
    except ConnectionError as e:
        print(f"最终失败：{e}")


# ── 策略二：JSON 安全提取 + 降级 ─────────────────────────────

def extract_json_safely(text: str, fallback: dict) -> dict:
    """
    从 LLM 输出中安全提取 JSON。
    LLM 有时会在 JSON 前后加说明文字，这个函数应对各种情况。
    全部失败时返回 fallback，绝不崩溃。
    """
    for marker_start, marker_end in [("```json", "```"), ("```", "```"), ("{", None)]:
        try:
            if marker_end:
                s = text.index(marker_start) + len(marker_start)
                e = text.index(marker_end, s)
                return json.loads(text[s:e].strip())
            else:
                s = text.index(marker_start)
                e = text.rindex("}") + 1
                return json.loads(text[s:e])
        except (ValueError, json.JSONDecodeError):
            continue
    print(f"  [降级] JSON 解析失败，使用默认值")
    return fallback


def demo_json_extraction() -> None:
    print("=== 演示二：JSON 安全提取 ===\n")
    messages = [
        system('从文本提取信息，输出 JSON：{"name": "姓名", "age": 年龄数字}'),
        user("我叫李华，今年30岁"),
    ]
    raw = chat(messages, temperature=0.1)
    print(f"  LLM 原始输出：{raw[:100]}")
    result = extract_json_safely(raw, fallback={"name": "未知", "age": 0})
    print(f"  提取结果：{result}")


# ── 策略三：流水线局部失败容忍 ───────────────────────────────

class ResilientPipeline:
    """
    可容忍局部失败的流水线。
    某一步失败时，不中断整体流程，而是用 fallback 内容继续。
    用户拿到的可能是"不完整结果"，但不会是"程序崩溃"。
    """

    def _run_step(self, step_name: str, messages: list[dict],
                  fallback: str, max_retries: int = 2) -> str:
        for attempt in range(1, max_retries + 1):
            try:
                result = chat(messages, temperature=0.5)
                if result.strip():
                    return result
            except Exception as e:
                print(f"  [{step_name}] 第{attempt}次失败：{e}")
                if attempt < max_retries:
                    time.sleep(0.3)
        print(f"  [{step_name}] 所有重试失败，使用降级内容")
        return fallback

    def run(self, topic: str) -> dict[str, str]:
        results: dict[str, str] = {}

        title = self._run_step(
            "标题生成",
            [system("为文章起一个吸引眼球的标题，只输出标题，不要加引号。"),
             user(f"主题：{topic}")],
            fallback=f"关于{topic}的思考",
        )
        results["title"] = title
        print(f"  [标题] {title}")

        summary = self._run_step(
            "摘要生成",
            [system("用一句话概括主题，不超过30字，直接输出。"),
             user(topic)],
            fallback="（摘要生成失败，请稍后查看）",
        )
        results["summary"] = summary
        print(f"  [摘要] {summary}")

        return results


def demo_pipeline() -> None:
    print("=== 演示三：流水线局部失败容忍 ===\n")
    pipeline = ResilientPipeline()
    result = pipeline.run("人工智能与未来就业")
    print(f"\n最终结果：{result}")


if __name__ == "__main__":
    demo_retry()
    print()
    demo_json_extraction()
    print()
    demo_pipeline()
