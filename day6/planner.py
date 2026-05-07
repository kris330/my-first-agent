import json
import re

from llm import chat

PLANNER_PROMPT = """你是一个任务规划专家。

用户给你一个复杂任务，把它分解成 3-6 个清晰、可执行的步骤。

可用工具：web_search（搜索）、get_weather（天气）、calculate（计算）、get_current_time（时间）

要求：
- 每步要具体，能直接执行
- 需要工具的步骤标明工具名，不需要的填 null
- 步骤数控制在 3-6 步，不要过多

返回 JSON 格式，不要加任何其他文字：
{
  "goal": "任务总目标一句话描述",
  "steps": [
    {"step": 1, "description": "具体步骤描述", "tool": "工具名或null"},
    {"step": 2, "description": "具体步骤描述", "tool": "工具名或null"}
  ]
}"""


def make_plan(task: str) -> dict:
    """为任务生成执行计划，返回计划字典。"""
    messages = [
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user",   "content": f"请为这个任务制定执行计划：{task}"},
    ]

    response = chat(messages)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # 尝试从文本中提取 JSON
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    # 解析失败，包装成单步计划
    return {
        "goal": task,
        "steps": [{"step": 1, "description": task, "tool": None}],
    }


def print_plan(plan: dict) -> None:
    """打印计划内容，给用户看。"""
    print(f"\n目标：{plan.get('goal', '未知')}")
    print(f"共 {len(plan.get('steps', []))} 步：")
    for step_info in plan.get("steps", []):
        tool_hint = f"  （工具：{step_info['tool']}）" if step_info.get("tool") else ""
        print(f"  步骤 {step_info['step']}：{step_info['description']}{tool_hint}")
