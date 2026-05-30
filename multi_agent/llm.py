"""多 Agent 进阶系列的 LLM 工具函数。"""
from __future__ import annotations

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def _make_client() -> OpenAI:
    kwargs: dict = {"api_key": os.environ["OPENAI_API_KEY"]}
    base_url = os.environ.get("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


_client = _make_client()
_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def chat(messages: list[dict], temperature: float = 0.7) -> str:
    """发送消息列表，返回 AI 回复文字。"""
    resp = _client.chat.completions.create(
        model=_model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def system(content: str) -> dict:
    return {"role": "system", "content": content}


def user(content: str) -> dict:
    return {"role": "user", "content": content}
