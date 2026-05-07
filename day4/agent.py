import json
import re

from llm import chat
from tool_registry import get_tools_description, execute_tool
from memory.short_term import ShortTermMemory

SYSTEM_PROMPT_TEMPLATE = """你是一个智能助手，可以使用工具，也能记住对话历史。

{tools_description}

每次回复必须是 JSON，格式二选一：

使用工具：
{{"action": "use_tool", "tool": "工具名", "params": {{"参数名": "参数值"}}}}

直接回答：
{{"action": "answer", "content": "你的回答"}}

参数名用英文，和工具定义完全一致。只返回 JSON。"""


def safe_parse_json(text: str) -> dict:
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
    return {"action": "answer", "content": text}


class Agent:
    def __init__(self) -> None:
        self.memory = ShortTermMemory(max_messages=20)
        self.memory.add("system", SYSTEM_PROMPT_TEMPLATE.format(
            tools_description=get_tools_description()
        ))

    def chat(self, user_input: str) -> str:
        self.memory.add("user", user_input)

        ai_response = chat(self.memory.to_api_format())
        print(f"[AI 决策]: {ai_response}")

        self.memory.add("assistant", ai_response)

        decision = safe_parse_json(ai_response)

        if decision["action"] == "answer":
            return decision.get("content", ai_response)

        if decision["action"] == "use_tool":
            tool_name = decision.get("tool", "")
            params    = decision.get("params", {})
            print(f"[执行工具]: {tool_name}，参数：{params}")
            tool_result = execute_tool(tool_name, params)
            print(f"[工具结果]: {tool_result}")

            # 把工具结果存入记忆，让 AI 知道发生了什么
            self.memory.add("user", f"[工具 {tool_name} 返回结果]：{tool_result}\n请基于此结果，用自然语言回答用户。")
            final = chat(self.memory.to_api_format())
            final_decision = safe_parse_json(final)
            final_text = final_decision.get("content", final)
            self.memory.add("assistant", final_text)
            return final_text

        return f"（未知 action：{decision.get('action')}）"

    def clear(self) -> None:
        self.memory.clear_non_system()

    def memory_count(self) -> int:
        return self.memory.message_count()
