from tools.search import web_search
from tools.weather import get_weather

# 工具注册表：工具名 → {函数, 描述, 参数说明}
TOOLS: dict[str, dict] = {
    "web_search": {
        "function": web_search,
        "description": "搜索互联网上的信息。适合查找新闻、事实、最新资讯。",
        "parameters": {
            "query": "搜索关键词，字符串类型，例如：'Python 教程'"
        },
    },
    "get_weather": {
        "function": get_weather,
        "description": "查询某个城市的天气情况。",
        "parameters": {
            "city": "城市名称，字符串类型，例如：北京、上海"
        },
    },
}


def get_tools_description() -> str:
    """生成给 AI 看的工具说明文字。"""
    lines = ["你有以下工具可以使用：\n"]
    for name, info in TOOLS.items():
        lines.append(f"工具名：{name}")
        lines.append(f"用途：{info['description']}")
        lines.append(f"参数：{info['parameters']}")
        lines.append("")
    return "\n".join(lines)


def execute_tool(tool_name: str, params: dict) -> str:
    """执行指定工具，返回结果字符串。"""
    if tool_name not in TOOLS:
        return f"没有这个工具：{tool_name!r}，可用工具：{list(TOOLS.keys())}"

    tool_func = TOOLS[tool_name]["function"]

    try:
        return str(tool_func(**params))
    except TypeError as e:
        return f"工具参数有误：{e}"
    except Exception as e:
        return f"工具执行出错：{e}"
