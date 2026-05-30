"""
进阶 Day 3 演示：Agent 间通信协议（Task / TaskResult）

统一任务交接的"格式"，解决两个问题：
  1. 接口统一：所有 Worker 的调用方式一致，增删 Worker 不影响 Orchestrator
  2. 可观测性：每次任务交接都有日志，出 bug 一眼就能定位

运行：
  cd multi_agent
  python adv3_protocol.py
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from llm import chat, system, user


# ── 协议定义 ──────────────────────────────────────────────────

class TaskStatus(Enum):
    DONE   = "done"
    FAILED = "failed"


@dataclass
class Task:
    """Orchestrator 下发给 Worker 的任务单。"""
    task_id:    str
    agent_name: str
    instruction: str
    context:    dict[str, Any] = field(default_factory=dict)
    created_at: float          = field(default_factory=time.time)


@dataclass
class TaskResult:
    """Worker 完成任务后回传给 Orchestrator 的结果单。"""
    task_id:     str
    agent_name:  str
    status:      TaskStatus
    output:      str
    duration_ms: int               = 0
    metadata:    dict[str, Any]    = field(default_factory=dict)

    @classmethod
    def success(cls, task: Task, output: str, **meta: Any) -> "TaskResult":
        ms = int((time.time() - task.created_at) * 1000)
        return cls(task.task_id, task.agent_name, TaskStatus.DONE, output, ms, dict(meta))

    @classmethod
    def failure(cls, task: Task, reason: str) -> "TaskResult":
        ms = int((time.time() - task.created_at) * 1000)
        return cls(task.task_id, task.agent_name, TaskStatus.FAILED, reason, ms)


# ── 协议日志器 ────────────────────────────────────────────────

class ProtocolLogger:
    """记录每次任务下发和结果接收，便于调试和追踪。"""

    def __init__(self) -> None:
        self._log: list[dict] = []

    def on_dispatch(self, task: Task) -> None:
        self._log.append({"event": "dispatch", "task_id": task.task_id,
                          "agent": task.agent_name, "instruction": task.instruction[:40]})
        print(f"  [协议] → 下发任务 {task.task_id[:8]} 给 {task.agent_name}")

    def on_result(self, result: TaskResult) -> None:
        self._log.append({"event": "result", "task_id": result.task_id,
                          "agent": result.agent_name, "status": result.status.value,
                          "duration_ms": result.duration_ms})
        icon = "✓" if result.status == TaskStatus.DONE else "✗"
        print(f"  [协议] {icon} 收到结果 {result.task_id[:8]} 来自 {result.agent_name} ({result.duration_ms}ms)")

    def print_summary(self) -> None:
        print("\n  --- 任务日志 ---")
        for entry in self._log:
            if entry["event"] == "dispatch":
                print(f"  下发: {entry['task_id'][:8]} → {entry['agent']}: {entry['instruction']}")
            else:
                status = entry["status"]
                print(f"  结果: {entry['task_id'][:8]} ← {entry['agent']} [{status}] {entry['duration_ms']}ms")


# ── 使用协议的 Agent ──────────────────────────────────────────

class KeywordExtractorAgent:
    """从文本中提取关键词。接口：run(task) -> TaskResult。"""

    def run(self, task: Task) -> TaskResult:
        messages = [
            system("从文本中提取3-5个核心关键词，用逗号分隔，只输出关键词。"),
            user(task.instruction),
        ]
        try:
            keywords = chat(messages, temperature=0.1)
            keyword_count = len(keywords.split(","))
            return TaskResult.success(task, output=keywords, keyword_count=keyword_count)
        except Exception as e:
            return TaskResult.failure(task, reason=str(e))


class TagGeneratorAgent:
    """根据关键词生成社交媒体话题标签。接口：run(task) -> TaskResult。"""

    def run(self, task: Task) -> TaskResult:
        keywords = task.context.get("keywords", "")
        messages = [
            system("根据关键词生成适合社交媒体的话题标签，格式：#标签1 #标签2，只输出标签。"),
            user(f"关键词：{keywords}"),
        ]
        try:
            tags = chat(messages, temperature=0.3)
            return TaskResult.success(task, output=tags)
        except Exception as e:
            return TaskResult.failure(task, reason=str(e))


# ── Orchestrator（使用协议）──────────────────────────────────

class ContentPipeline:
    """
    内容处理流水线：
      1. 关键词提取
      2. 话题标签生成（用关键词作为输入）
    每步都通过协议交接，有完整的日志记录。
    """

    def __init__(self) -> None:
        self._extractor = KeywordExtractorAgent()
        self._tagger    = TagGeneratorAgent()
        self._logger    = ProtocolLogger()

    def run(self, article: str) -> dict[str, Any]:
        print("\n[Pipeline] 启动内容处理流水线")

        # Step 1：关键词提取
        t1 = Task(task_id=str(uuid.uuid4()), agent_name="keyword_extractor",
                  instruction=article)
        self._logger.on_dispatch(t1)
        r1 = self._extractor.run(t1)
        self._logger.on_result(r1)

        if r1.status == TaskStatus.FAILED:
            return {"error": f"关键词提取失败：{r1.output}"}

        # Step 2：话题标签（把关键词放进 context 传过去）
        t2 = Task(task_id=str(uuid.uuid4()), agent_name="tag_generator",
                  instruction="生成话题标签",
                  context={"keywords": r1.output})
        self._logger.on_dispatch(t2)
        r2 = self._tagger.run(t2)
        self._logger.on_result(r2)

        self._logger.print_summary()

        return {
            "keywords":     r1.output,
            "tags":         r2.output if r2.status == TaskStatus.DONE else "",
            "total_ms":     r1.duration_ms + r2.duration_ms,
            "keyword_count": r1.metadata.get("keyword_count", 0),
        }


if __name__ == "__main__":
    article = (
        "近日，多家科技公司相继发布了新一代 AI 芯片，性能较上一代提升了3倍。"
        "这些芯片专为大模型训练和推理优化，能耗大幅降低。"
        "业内人士认为，这将推动 AI 应用的大规模普及。"
    )

    pipeline = ContentPipeline()
    result = pipeline.run(article)

    print(f"\n关键词：{result.get('keywords', '')}")
    print(f"标签：  {result.get('tags', '')}")
    print(f"总耗时：{result.get('total_ms', 0)}ms")
