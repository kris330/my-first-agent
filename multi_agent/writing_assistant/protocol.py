"""
Agent 间通信协议：Task / TaskResult。

所有 Worker Agent 只通过这两个数据类与 Orchestrator 交换信息，
保持松耦合——增删 Worker 不影响其他模块。
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    DONE = "done"
    FAILED = "failed"


@dataclass
class Task:
    """Orchestrator 下发给 Worker Agent 的任务单。"""

    task_id: str
    agent_name: str
    instruction: str
    context: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    @classmethod
    def new(cls, agent_name: str, instruction: str, **context: Any) -> "Task":
        """快捷工厂方法：自动生成 task_id。"""
        return cls(
            task_id=str(uuid.uuid4())[:8],
            agent_name=agent_name,
            instruction=instruction,
            context=dict(context),
        )


@dataclass
class TaskResult:
    """Worker Agent 完成任务后回传给 Orchestrator 的结果单。"""

    task_id: str
    agent_name: str
    status: TaskStatus
    output: str
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(cls, task: Task, output: str, **metadata: Any) -> "TaskResult":
        """成功结果工厂方法，自动计算耗时。"""
        ms = int((time.time() - task.created_at) * 1000)
        return cls(
            task_id=task.task_id,
            agent_name=task.agent_name,
            status=TaskStatus.DONE,
            output=output,
            duration_ms=ms,
            metadata=dict(metadata),
        )

    @classmethod
    def failure(cls, task: Task, reason: str) -> "TaskResult":
        """失败结果工厂方法，自动计算耗时。"""
        ms = int((time.time() - task.created_at) * 1000)
        return cls(
            task_id=task.task_id,
            agent_name=task.agent_name,
            status=TaskStatus.FAILED,
            output=reason,
            duration_ms=ms,
        )

    @property
    def ok(self) -> bool:
        return self.status == TaskStatus.DONE
