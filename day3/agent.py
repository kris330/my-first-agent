import json
import re

from llm import chat
from tool_registry import get_tools_description, execute_tool


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


def build_system_prompt() -> str:
    return f"""你是一个智能助手，可以使用多种工具。

{get_tools_description()}
根据用户的问题，选择合适的工具，或者直接回答。

回复必须是 JSON，格式二选一：

使用工具：
{{"action": "use_tool", "tool": "工具名", "params": {{"参数名": "参数值"}}}}

直接回答：
{{"action": "answer", "content": "你的回答"}}

参数名必须用英文，和工具定义完全一致。
只返回 JSON，不加任何解释。"""


def run_agent(user_input: str) -> str:
    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user",   "content": user_input},
    ]

    ai_response = chat(messages)
    print(f"[AI 决策]: {ai_response}")

    decision = safe_parse_json(ai_response)

    if decision["action"] == "answer":
        return decision.get("content", ai_response)

    if decision["action"] == "use_tool":
        tool_name = decision.get("tool", "")
        params    = decision.get("params", {})
        print(f"[执行工具]: {tool_name}，参数：{params}")
        result = execute_tool(tool_name, params)
        print(f"[工具结果]: {result}")
        return result

    return f"（未知 action：{decision.get('action')}）"
