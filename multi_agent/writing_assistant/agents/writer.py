"""
写作 Agent：根据研究报告，生成完整文章初稿。

对应进阶 Day 2：Worker Agent 之间的上下文传递。
"""
from __future__ import annotations

from llm import chat, system, user
from protocol import Task, TaskResult

_SYSTEM_PROMPT = """\
你是一位经验丰富的内容创作者，擅长将复杂知识写成清晰易懂的文章。

写作原则：
- 开篇用一个具体场景或问题抓住读者
- 逻辑清晰，每段只围绕一个核心观点展开
- 用类比和例子解释抽象概念，让普通读者也能看懂
- 结尾给读者留下明确的思考方向或行动建议
- 语言自然流畅，避免"首先、其次、最后"等套话

直接输出文章正文，不要加任何说明性前缀。
"""


class WriterAgent:
    """写作员：根据研究报告写出文章初稿。"""

    def run(self, task: Task) -> TaskResult:
        topic = task.instruction
        research = task.context.get("research_output", "（无研究资料）")
        prompt = f"""\
写作主题：{topic}

以下是研究员整理的参考资料，请基于这些内容写出完整文章：

{research}

直接输出文章正文。
"""
        messages = [system(_SYSTEM_PROMPT), user(prompt)]
        try:
            draft = chat(messages, temperature=0.8)
            return TaskResult.success(task, output=draft)
        except Exception as e:
            return TaskResult.failure(task, reason=str(e))
