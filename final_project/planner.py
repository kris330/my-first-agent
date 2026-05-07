import json
import re

from llm import chat

PLANNER_PROMPT = """你是一个任务规划专家。

用户给你一个复杂任务，把它分解成 3-6 个清晰、可执行的步骤。

可用工具：web_search（搜索）、get_weather（天气）、calculate（计算）、get_current_time（时间）

要求：
- 每步要具体，能直接执行
- 需要工具的步骤标明工具名，不需要的填 null
- 步骤数控制在 3-6 步

只返回 JSON，不要加任何其他文字：
{
  "goal": "任务总目标一句话描述",
  "steps": [
    {"step": 1, "description": "具体步骤描述", "tool": "工具名或null"},
    {"step": 2, "description": "具体步骤描述", "tool": "工具名或null"}
  ]
}"""


def make_plan(task: str) -> dict:
    """为任务生成执行计划。"""
    response = chat([
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user",   "content": f"请为这个任务制定执行计划：{task}"},
    ])

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    return {"goal": task, "steps": [{"step": 1, "description": task, "tool": None}]}


def print_plan(plan: dict) -> None:
    print(f"\n目标：{plan.get('goal', '未知')}")
    steps = plan.get("steps", [])
    print(f"共 {len(steps)} 步：")
    for s in steps:
        tool_hint = f"  （工具：{s['tool']}）" if s.get("tool") else ""
        print(f"  步骤 {s['step']}：{s['description']}{tool_hint}")
