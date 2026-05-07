import json
import re

from llm import chat
from tool_registry import execute_tool


def _infer_params(tool_name: str, step_desc: str, goal: str) -> dict:
    """让 AI 根据步骤描述推断工具参数。"""
    prompt = (
        f"任务总目标：{goal}\n"
        f"当前步骤：{step_desc}\n"
        f"需要调用工具：{tool_name}\n\n"
        f"请生成调用该工具所需的参数，只返回 JSON 对象，不要任何其他文字。\n"
        f"例如：{{\"query\": \"搜索关键词\"}}"
    )
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
    """按计划逐步执行，汇总后生成最终答案。"""
    goal  = plan.get("goal", "未知任务")
    steps = plan.get("steps", [])

    print(f"\n开始执行计划：{goal}")
    results: list[str] = []

    for s in steps:
        step_num  = s["step"]
        desc      = s["description"]
        tool_name = s.get("tool")

        print(f"\n{'─'*40}")
        print(f"步骤 {step_num}：{desc}")

        if tool_name:
            params = _infer_params(tool_name, desc, goal)
            print(f"[调用工具 {tool_name}]，参数：{params}")
            result  = execute_tool(tool_name, params)
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"[结果]: {preview}")
        else:
            result = chat([{
                "role": "user",
                "content": f"请完成这个步骤：{desc}\n（这是任务「{goal}」的一部分）",
            }])
            print(f"[AI 完成]: {result[:200]}...")

        results.append(f"步骤{step_num}（{desc}）：\n{result}")

    print(f"\n{'─'*40}")
    print("[整合所有结果，生成最终答案...]")

    summary = chat([{
        "role": "user",
        "content": (
            f"你完成了任务：{goal}\n\n"
            f"以下是每个步骤的执行结果：\n"
            f"{'='*20}\n"
            f"{chr(10).join(results)}\n"
            f"{'='*20}\n\n"
            f"请基于以上信息，给用户一个完整、清晰、结构化的最终答案。"
        ),
    }])
    return summary
