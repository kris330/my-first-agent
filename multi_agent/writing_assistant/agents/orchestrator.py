"""
调度员 Agent（Orchestrator）：驱动 Researcher → Writer → Editor 流水线。

整合了进阶篇核心概念：
- Orchestrator + Worker 架构（进阶 Day 2）
- Task / TaskResult 协议（进阶 Day 3）
- 每步最多重试 2 次，失败时打印错误并继续（进阶 Day 5）
"""
from __future__ import annotations

import time

from agents.editor import EditorAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from protocol import Task, TaskResult, TaskStatus


class OrchestratorAgent:
    """调度员：不生成内容，只负责拆解、传递和汇总。"""

    MAX_RETRIES = 2

    def __init__(self) -> None:
        self._researcher = ResearcherAgent()
        self._writer = WriterAgent()
        self._editor = EditorAgent()

    def run(self, user_request: str) -> str:
        """
        接收用户请求，返回最终文章。

        流程：Research → Write → Edit
        每步的输出自动成为下一步的输入（Context 传递）。
        """
        print(f"\n[Orchestrator] 收到任务：{user_request}")

        # Step 1: 研究
        print("[Orchestrator] → 交给 Researcher...")
        research_result = self._run_with_retry(
            agent=self._researcher,
            agent_name="researcher",
            instruction=user_request,
        )
        if research_result.status == TaskStatus.FAILED:
            return f"研究阶段失败：{research_result.output}"
        print(f"[Orchestrator]   Researcher 完成（{research_result.duration_ms}ms）")

        # Step 2: 写作（携带研究报告）
        print("[Orchestrator] → 交给 Writer...")
        write_result = self._run_with_retry(
            agent=self._writer,
            agent_name="writer",
            instruction=user_request,
            research_output=research_result.output,
        )
        if write_result.status == TaskStatus.FAILED:
            return f"写作阶段失败：{write_result.output}"
        print(f"[Orchestrator]   Writer 完成（{write_result.duration_ms}ms）")

        # Step 3: 编辑（携带初稿）
        print("[Orchestrator] → 交给 Editor...")
        edit_result = self._run_with_retry(
            agent=self._editor,
            agent_name="editor",
            instruction=user_request,
            draft=write_result.output,
        )
        if edit_result.status == TaskStatus.FAILED:
            print(f"[Orchestrator]   Editor 失败，保留初稿。")
            return write_result.output
        print(f"[Orchestrator]   Editor 完成（{edit_result.duration_ms}ms）")

        print("[Orchestrator] 全部流程完成。\n")
        return edit_result.output

    def _run_with_retry(
        self,
        agent: ResearcherAgent | WriterAgent | EditorAgent,
        agent_name: str,
        instruction: str,
        **context_kwargs: str,
    ) -> TaskResult:
        """
        执行单个 Agent，失败时最多重试 MAX_RETRIES 次。
        每次重试间隔 1 秒，失败时打印错误继续（不崩溃）。
        对应进阶 Day 5 的重试策略。
        """
        last_result: TaskResult | None = None
        for attempt in range(1, self.MAX_RETRIES + 2):  # +2 = 1次正常 + MAX_RETRIES次重试
            task = Task.new(
                agent_name=agent_name,
                instruction=instruction,
                **context_kwargs,
            )
            result = agent.run(task)
            if result.status == TaskStatus.DONE:
                return result

            last_result = result
            if attempt <= self.MAX_RETRIES:
                print(f"  [{agent_name}] 第{attempt}次失败：{result.output}，1s 后重试...")
                time.sleep(1)
            else:
                print(f"  [{agent_name}] 已达最大重试次数，放弃。")

        return last_result  # type: ignore[return-value]
