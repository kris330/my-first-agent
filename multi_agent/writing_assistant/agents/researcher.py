"""
研究员 Agent：分析写作主题，整理关键要点和写作建议。

对应进阶 Day 2：Worker Agent 的职责划分。
"""
from __future__ import annotations

from llm import chat, system, user
from protocol import Task, TaskResult

_SYSTEM_PROMPT = """\
你是一位经验丰富的内容研究员。
用户会给你一个写作主题，你的任务是：
1. 分析该主题的核心角度和背景
2. 整理出 5-8 个读者最需要了解的关键要点
3. 给出写作方向建议：受众定位、行文语气、重点突出哪些方面

直接输出分析内容，自然流畅地表达，不需要 JSON 格式。
"""


class ResearcherAgent:
    """研究员：给定主题，返回背景资料和写作要点。"""

    def run(self, task: Task) -> TaskResult:
        topic = task.instruction
        prompt = f"写作主题：{topic}\n\n请帮我分析这个主题，整理关键要点和写作建议。"
        messages = [system(_SYSTEM_PROMPT), user(prompt)]
        try:
            output = chat(messages, temperature=0.3)
            return TaskResult.success(task, output=output)
        except Exception as e:
            return TaskResult.failure(task, reason=str(e))
