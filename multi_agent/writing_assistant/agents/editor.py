"""
编辑 Agent：审核文章初稿，给出最重要的改进建议，并直接输出改进版全文。

对应进阶 Day 2：流水线最后一环的输出规范。
"""
from __future__ import annotations

from llm import chat, system, user
from protocol import Task, TaskResult

_SYSTEM_PROMPT = """\
你是一位严格但高效的文章编辑。

你的工作分两步：
1. 给出【一条】最重要的改进建议（一句话，直接说问题在哪、怎么改）
2. 紧接着输出改进后的完整文章全文

输出格式：
【改进建议】<一句话建议>

【终稿】
<改进后的完整文章>

不要列多条建议，聚焦最关键的一条，然后在终稿中把它改好。
"""


class EditorAgent:
    """编辑：审核初稿，输出改进建议 + 终稿。"""

    def run(self, task: Task) -> TaskResult:
        draft = task.context.get("draft", "")
        topic = task.instruction
        prompt = f"""\
文章主题：{topic}

以下是初稿，请审核并改进：

{draft}
"""
        messages = [system(_SYSTEM_PROMPT), user(prompt)]
        try:
            response = chat(messages, temperature=0.4)
            final = _extract_final(response)
            return TaskResult.success(task, output=final, full_response=response)
        except Exception as e:
            return TaskResult.failure(task, reason=str(e))


def _extract_final(editor_response: str) -> str:
    """从编辑器响应中提取【终稿】部分。"""
    marker = "【终稿】"
    if marker in editor_response:
        return editor_response[editor_response.index(marker) + len(marker):].strip()
    return editor_response.strip()
