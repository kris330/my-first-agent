import os
from openai import OpenAI
from config import get_model, get_base_url

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        kwargs: dict = {"api_key": os.environ["OPENAI_API_KEY"]}
        base_url = get_base_url()
        if base_url:
            kwargs["base_url"] = base_url
        _client = OpenAI(**kwargs)
    return _client


def chat(messages: list[dict]) -> str:
    """发送消息列表给 AI，返回回复文字。"""
    response = _get_client().chat.completions.create(
        model=get_model(),
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
