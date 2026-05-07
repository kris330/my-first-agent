import json
import re

from llm import chat
from tool_registry import get_tools_description, execute_tool
from memory.short_term import ShortTermMemory

REACT_SYSTEM_PROMPT = """你是一个智能助手，拥有对话记忆，可以使用工具完成任务。

{tools_description}
每次回复必须是 JSON，三种格式之一：

1. 需要使用工具：
{{"type": "tool_call", "tool": "工具名", "params": {{"参数名": "参数值"}}, "thought": "我为什么要用这个工具"}}

2. 任务完成或可以直接回答：
{{"type": "final_answer", "content": "回答内容"}}

3. 需要向用户提问：
{{"type": "ask_user", "question": "你的问题"}}

规则：
- 最多使用工具 {max_steps} 次
- 收集到足够信息后，必须给出 final_answer
- 不要用相同参数重复调用同一个工具
- 参数名必须用英文，和工具定义完全一致
- 只返回 JSON，不加任何解释"""


def _safe_parse(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"type": "final_answer", "content": text}


class ReactAgent:
    """
    带对话记忆的 ReAct Agent。
    同一个实例跨多次 run() 调用时共享记忆（多轮对话）。
    """

    def __init__(self, max_steps: int = 5) -> None:
        self.max_steps = max_steps
        self._memory   = ShortTermMemory(max_messages=30)
        self._memory.add("system", REACT_SYSTEM_PROMPT.format(
            tools_description=get_tools_description(),
            max_steps=max_steps,
        ))

    def run(self, user_input: str) -> str:
        """处理一条用户输入，返回最终回答。保留对话记忆。"""
        self._memory.add("user", user_input)

        for step in range(1, self.max_steps + 1):
            print(f"\n{'─'*40}")
            print(f"[步骤 {step}/{self.max_steps}]")

            ai_response = chat(self._memory.to_api_format())
            print(f"[AI 思考]: {ai_response}")
            self._memory.add("assistant", ai_response)

            decision  = _safe_parse(ai_response)
            resp_type = decision.get("type")

            if resp_type == "final_answer":
                print(f"[完成，共 {step} 步]")
                return decision.get("content", "（无内容）")

            if resp_type == "tool_call":
                tool_name = decision.get("tool", "")
                params    = decision.get("params", {})
                thought   = decision.get("thought", "")
                print(f"[调用工具]: {tool_name}，参数：{params}")
                if thought:
                    print(f"[理由]: {thought}")
                result  = execute_tool(tool_name, params)
                preview = result[:300] + "..." if len(result) > 300 else result
                print(f"[工具结果]: {preview}")
                self._memory.add("user", f"工具 {tool_name} 返回：\n{result}")
                continue

            if resp_type == "ask_user":
                answer = input(f"\nAgent 问你：{decision.get('question', '')}\n你：")
                self._memory.add("user", answer)
                continue

            return str(decision)

        # 步骤用完，强制收尾
        self._memory.add("user", "已达步骤上限，请立即给出最终答案。")
        final = chat(self._memory.to_api_format())
        parsed = _safe_parse(final)
        answer = parsed.get("content", final)
        self._memory.add("assistant", answer)
        return answer

    def clear_memory(self) -> None:
        self._memory.clear_non_system()

    def memory_count(self) -> int:
        return self._memory.count()
