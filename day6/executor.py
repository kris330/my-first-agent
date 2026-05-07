import json
import re

from llm import chat
from tool_registry import execute_tool


def _generate_tool_params(tool_name: str, step_description: str, goal: str) -> dict:
    """让 AI 根据步骤描述生成工具参数。"""
    prompt = f"""任务总目标：{goal}
当前步骤：{step_description}
需要调用工具：{tool_name}

请生成调用该工具所需的参数，只返回 JSON 对象，不要任何其他文字。
例如对于 web_search：{{"query": "搜索关键词"}}"""

    response = chat([{"role": "user", "content": prompt}])

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {}


def execute_plan(plan: dict) -> str:
    """按计划逐步执行，最终汇总成完整答案。"""
    goal  = plan.get("goal", "未知任务")
    steps = plan.get("steps", [])

    print(f"\n开始执行计划：{goal}")
    collected_results: list[str] = []

    for step_info in steps:
        step_num    = step_info["step"]
        description = step_info["description"]
        tool_name   = step_info.get("tool")

        print(f"\n{'─'*40}")
        print(f"步骤 {step_num}：{description}")

        if tool_name:
            params = _generate_tool_params(tool_name, description, goal)
            print(f"[调用工具 {tool_name}]，参数：{params}")
            result = execute_tool(tool_name, params)
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"[结果]: {preview}")
        else:
            # 不需要工具，直接让 AI 处理这一步
            result = chat([{
                "role": "user",
                "content": f"请完成这个步骤：{description}\n（这是任务「{goal}」的一部分）"
            }])
            print(f"[AI 完成]: {result[:200]}...")

        collected_results.append(f"步骤{step_num}（{description}）：\n{result}")

    # 整合所有步骤结果，生成最终答案
    print(f"\n{'─'*40}")
    print("[整合所有结果，生成最终答案...]")

    summary_prompt = f"""你完成了任务：{goal}

以下是每个步骤的执行结果：
{'='*20}
{chr(10).join(collected_results)}
{'='*20}

请基于以上所有信息，给用户一个完整、清晰、结构化的最终答案。"""

    return chat([{"role": "user", "content": summary_prompt}])
