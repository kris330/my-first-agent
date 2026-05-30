"""
进阶 Day 4 演示：串行 vs 并行任务流

场景：让三个 Agent 从不同角度分析同一篇文章，
对比串行执行和并行执行的时间差距。

运行：
  cd multi_agent
  python adv4_parallel.py
"""
from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from llm import chat, system, user


# ── 复用 Day 3 的协议数据结构 ────────────────────────────────

class TaskStatus(Enum):
    DONE   = "done"
    FAILED = "failed"


@dataclass
class Task:
    task_id:     str
    agent_name:  str
    instruction: str
    context:     dict[str, Any] = field(default_factory=dict)
    created_at:  float          = field(default_factory=time.time)


@dataclass
class TaskResult:
    task_id:     str
    agent_name:  str
    status:      TaskStatus
    output:      str
    duration_ms: int = 0

    @classmethod
    def success(cls, task: Task, output: str) -> "TaskResult":
        ms = int((time.time() - task.created_at) * 1000)
        return cls(task.task_id, task.agent_name, TaskStatus.DONE, output, ms)

    @classmethod
    def failure(cls, task: Task, reason: str) -> "TaskResult":
        ms = int((time.time() - task.created_at) * 1000)
        return cls(task.task_id, task.agent_name, TaskStatus.FAILED, reason, ms)


# ── 通用分析 Worker ───────────────────────────────────────────

class AnalysisWorker:
    """通用分析 Worker，由 system_prompt 决定分析角度。"""

    def __init__(self, name: str, prompt: str) -> None:
        self.name = name
        self._prompt = prompt

    def run(self, task: Task) -> TaskResult:
        messages = [
            system(self._prompt),
            user(task.instruction),
        ]
        try:
            output = chat(messages, temperature=0.4)
            return TaskResult.success(task, output)
        except Exception as e:
            return TaskResult.failure(task, str(e))


def make_analysis_workers() -> list[AnalysisWorker]:
    return [
        AnalysisWorker(
            "fact_checker",
            "你是事实核查员。找出文章中可能存在争议或需要验证的说法，用2-3句话说明。"
        ),
        AnalysisWorker(
            "tone_analyst",
            "你是语言风格分析师。分析文章的写作风格、语气和目标读者，用2-3句话描述。"
        ),
        AnalysisWorker(
            "action_advisor",
            "你是行动建议顾问。根据文章内容，给读者提出1-2个具体可行的行动建议。"
        ),
    ]


# ── 串行执行 ──────────────────────────────────────────────────

def run_serial(article: str, workers: list[AnalysisWorker]) -> tuple[list[TaskResult], float]:
    start = time.time()
    results = []
    for w in workers:
        task = Task(task_id=str(uuid.uuid4()), agent_name=w.name, instruction=article)
        result = w.run(task)
        results.append(result)
        print(f"  [串行] {w.name} 完成 ({result.duration_ms}ms)")
    return results, time.time() - start


# ── 并行执行 ──────────────────────────────────────────────────

def run_parallel(article: str, workers: list[AnalysisWorker]) -> tuple[list[TaskResult], float]:
    start = time.time()
    results: list[TaskResult] = []

    with ThreadPoolExecutor(max_workers=len(workers)) as executor:
        futures = {
            executor.submit(
                w.run,
                Task(task_id=str(uuid.uuid4()), agent_name=w.name, instruction=article)
            ): w.name
            for w in workers
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"  [并行] {result.agent_name} 完成 ({result.duration_ms}ms)")

    return results, time.time() - start


# ── Synthesizer：汇总多个分析结果 ───────────────────────────

def synthesize(article: str, results: list[TaskResult]) -> str:
    """把多份分析结果合并成一段综合报告。"""
    analyses = "\n\n".join(
        f"【{r.agent_name}】\n{r.output}"
        for r in results
        if r.status == TaskStatus.DONE
    )
    messages = [
        system("你是报告整合者，将多份分析整合为一段连贯的综合评估，不超过100字。"),
        user(f"原文（节选）：{article[:150]}...\n\n各方分析：\n{analyses}"),
    ]
    return chat(messages, temperature=0.4)


if __name__ == "__main__":
    article = (
        "研究显示，每天阅读30分钟的人，5年后的词汇量比不阅读的人高出23%，"
        "决策能力也显著提升。然而，超过60%的成年人每天阅读时间不足15分钟。"
        "专家建议，将手机通知关闭、在固定时间阅读，是建立阅读习惯最有效的方法。"
    )

    print("=== 串行执行（一个接一个）===")
    serial_results, serial_time = run_serial(article, make_analysis_workers())
    print(f"总耗时：{serial_time:.2f}s\n")

    print("=== 并行执行（同时开干）===")
    parallel_results, parallel_time = run_parallel(article, make_analysis_workers())
    print(f"总耗时：{parallel_time:.2f}s")
    if parallel_time > 0:
        print(f"加速比：{serial_time / parallel_time:.1f}x\n")

    print("=== 综合报告 ===")
    report = synthesize(article, parallel_results)
    print(report)
