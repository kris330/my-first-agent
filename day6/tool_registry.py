from tools.search import web_search
from tools.weather import get_weather
from tools.calculator import calculate
from tools.datetime_tool import get_current_time

TOOLS: dict[str, dict] = {
    "web_search":       {"function": web_search,       "description": "搜索互联网信息。",      "parameters": {"query": "搜索关键词"}},
    "get_weather":      {"function": get_weather,       "description": "查询城市天气。",        "parameters": {"city": "城市名称"}},
    "calculate":        {"function": calculate,         "description": "计算数学表达式。",      "parameters": {"expression": "数学表达式字符串"}},
    "get_current_time": {"function": get_current_time,  "description": "获取当前时间。",        "parameters": {"timezone": "时区名，默认 Asia/Shanghai"}},
}


def get_tools_description() -> str:
    lines = ["你有以下工具：\n"]
    for name, info in TOOLS.items():
        lines.append(f"工具名：{name}  用途：{info['description']}  参数：{info['parameters']}")
    return "\n".join(lines)


def execute_tool(tool_name: str, params: dict) -> str:
    if tool_name not in TOOLS:
        return f"没有这个工具：{tool_name!r}"
    try:
        return str(TOOLS[tool_name]["function"](**params))
    except TypeError as e:
        return f"工具参数有误：{e}"
    except Exception as e:
        return f"工具执行出错：{e}"
