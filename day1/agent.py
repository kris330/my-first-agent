from llm import chat

SYSTEM_PROMPT = """你是一个智能助手。

当用户问你问题时，判断：是直接回答，还是需要查天气。

你必须用 JSON 格式回复，不能说任何其他话。

格式如下：

如果可以直接回答：
{"action": "answer", "content": "你的回答内容"}

如果需要查天气：
{"action": "get_weather", "city": "城市名"}

只返回 JSON，不要加任何解释、前缀或代码块标记。"""


def run_agent(user_input: str) -> str:
    """让 AI 决定如何响应用户，返回 AI 的原始 JSON 回复。"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_input},
    ]

    response = chat(messages)
    print(f"[AI 决策]: {response}")  # 调试用，让你看到 AI 在想什么
    return response
