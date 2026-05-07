import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    # 如果用国内 API，取消下面这行注释并填入对应地址：
    # base_url="https://api.deepseek.com",
)


def chat(messages: list[dict]) -> str:
    """
    发送消息列表给 AI，返回 AI 的回复文字。

    messages 格式：
    [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user",   "content": "你好"},
    ]
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 便宜好用；国内 API 改成对应模型名
        messages=messages,
        temperature=0,        # 0 = 输出更稳定
    )
    return response.choices[0].message.content
