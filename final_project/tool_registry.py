from tools.search import web_search
from tools.weather import get_weather
from tools.calculator import calculate
from tools.datetime_tool import get_current_time

# 工具注册表。新增工具：写函数 → 加一条记录 → 完成。
TOOLS: dict[str, dict] = {
    "web_search": {
        "function": web_search,
        "description": "搜索互联网信息。适合查找新闻、事实、最新资讯、人物介绍。",
        "parameters": {"query": "搜索关键词，字符串"},
    },
    "get_weather": {
        "function": get_weather,
        "description": "查询某个城市的天气情况。",
        "parameters": {"city": "城市名称，字符串，例如：北京"},
    },
    "calculate": {
        "function": calculate,
        "description": "计算数学表达式，支持加减乘除和括号。不适合搜索或文字类问题。",
        "parameters": {"expression": "数学表达式字符串，例如：(3+5)*2"},
    },
    "get_current_time": {
        "function": get_current_time,
        "description": "获取当前日期和时间。",
        "parameters": {"timezone": "时区名称，字符串，默认 Asia/Shanghai"},
    },
}


def get_tools_description() -> str:
    lines = ["你有以下工具可以使用：\n"]
    for name, info in TOOLS.items():
        lines.append(f"工具名：{name}")
        lines.append(f"用途：{info['description']}")
        lines.append(f"参数：{info['parameters']}")
        lines.append("")
    return "\n".join(lines)


def execute_tool(tool_name: str, params: dict) -> str:
    if tool_name not in TOOLS:
        available = list(TOOLS.keys())
        return f"没有这个工具：{tool_name!r}，可用工具：{available}"
    try:
        return str(TOOLS[tool_name]["function"](**params))
    except TypeError as e:
        return f"工具参数有误：{e}"
    except Exception as e:
        return f"工具执行出错：{e}"
