import json
import re


def get_weather(city: str) -> str:
    """今天用模拟数据，Day2 换成真实 API。"""
    mock_data = {
        "北京": "晴，15°C，东风3级",
        "上海": "多云，18°C，南风2级",
        "广州": "小雨，22°C，偏东风",
        "深圳": "阴，24°C，东南风2级",
        "成都": "多云，16°C，微风",
    }
    return mock_data.get(city, f"{city}：晴，20°C（模拟数据）")


def safe_parse_json(text: str) -> dict:
    """从 AI 回复里提取 JSON，即使 AI 多说了废话也能处理。"""
    # 先尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试从文本里找 {...} 块
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 兜底：把原文当作普通回答
    return {"action": "answer", "content": text}


def execute_action(ai_response: str) -> str:
    """解析 AI 返回的 JSON，执行对应动作。"""
    decision = safe_parse_json(ai_response)
    action = decision.get("action")

    if action == "answer":
        return decision.get("content", "（AI 没有提供内容）")

    elif action == "get_weather":
        city = decision.get("city", "未知城市")
        weather = get_weather(city)
        return f"{city}的天气：{weather}"

    else:
        # AI 返回了不认识的动作，直接把内容输出
        return f"（未知动作 {action!r}）{decision}"
