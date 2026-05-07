import json
import re

from llm import chat
from tool_registry import get_tools_description, execute_tool
from memory.short_term import ShortTermMemory

REACT_SYSTEM_PROMPT = """你是一个能完成复杂任务的智能助手，可以反复使用工具直到任务完成。

{tools_description}

每次回复必须是 JSON，三种格式之一：

1. 需要使用工具：
{{"type": "tool_call", "tool": "工具名", "params": {{"参数名": "参数值"}}, "thought": "我为什么要用这个工具"}}

2. 任务完成，给出最终答案：
{{"type": "final_answer", "content": "最终答案内容"}}

3. 需要向用户提问：
{{"type": "ask_user", "question": "你的问题"}}

规则：最多 {max_steps} 步，收集到足够信息后给出 final_answer，不重复调用相同参数的工具。
只返回 JSON。"""


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
    return {"type": "final_answer", "content": text}


class ReactAgent:
    def __init__(self, max_steps: int = 5) -> None:
        self.max_steps = max_steps

    def run(self, user_task: str) -> str:
        memory = ShortTermMemory(max_messages=40)
        memory.add("system", REACT_SYSTEM_PROMPT.format(
            tools_description=get_tools_description(),
            max_steps=self.max_steps,
        ))
        memory.add("user", f"请帮我完成这个任务：{user_task}")

        for step in range(1, self.max_steps + 1):
            print(f"\n{'─'*40}")
            print(f"[步骤 {step}/{self.max_steps}]")
            ai_response = chat(memory.to_api_format())
            print(f"[AI 思考]: {ai_response}")
            memory.add("assistant", ai_response)
            decision = safe_parse_json(ai_response)
            resp_type = decision.get("type")

            if resp_type == "final_answer":
                print(f"[任务完成，共 {step} 步]")
                return decision.get("content", "（无内容）")

            if resp_type == "tool_call":
                tool_name = decision.get("tool", "")
                params    = decision.get("params", {})
                print(f"[调用工具]: {tool_name}，参数：{params}")
                result  = execute_tool(tool_name, params)
                preview = result[:300] + "..." if len(result) > 300 else result
                print(f"[工具结果]: {preview}")
                memory.add("user", f"工具 {tool_name} 返回：\n{result}")
                continue

            if resp_type == "ask_user":
                answer = input(f"\nAgent 问你：{decision.get('question', '')}\n你：")
                memory.add("user", answer)
                continue

            return str(decision)

        memory.add("user", "你已用完所有步骤，请立即给出最终答案。")
        final = chat(memory.to_api_format())
        parsed = safe_parse_json(final)
        return parsed.get("content", final)
