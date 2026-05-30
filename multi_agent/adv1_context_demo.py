"""
进阶 Day 1 演示：单 Agent 上下文膨胀 vs 多 Agent 上下文隔离

运行：
  cd multi_agent
  python adv1_context_demo.py
"""
from __future__ import annotations

from llm import chat, system, user


def estimate_tokens(messages: list[dict]) -> int:
    """粗略估算 token 数（中文约 1.5 字/token）。"""
    total_chars = sum(len(str(m.get("content", ""))) for m in messages)
    return int(total_chars / 1.5)


def demo_single_agent() -> None:
    """演示单 Agent 包干所有事时，上下文如何快速增长。"""
    print("=== 场景一：一个 Agent 包干所有事 ===\n")

    messages = [system("你是一个全能助手，负责研究、写作、审核全部环节。")]

    steps = [
        ("研究阶段", "研究'人工智能'主题，列出3个核心概念，每条一句话。"),
        ("结构规划", "基于研究，给出一篇科普文章的3段式大纲，每段标题加一句说明。"),
        ("写作阶段", "按大纲写出文章正文，约200字。"),
        ("审核阶段", "指出文章最主要的1个问题并给出改进建议。"),
    ]

    for step_name, instruction in steps:
        messages.append(user(instruction))
        tokens_before = estimate_tokens(messages)
        reply = chat(messages, temperature=0.7)
        messages.append({"role": "assistant", "content": reply})
        tokens_after = estimate_tokens(messages)
        print(f"[{step_name}]  {tokens_before:,} → {tokens_after:,} tokens  (+{tokens_after - tokens_before:,})")

    final = estimate_tokens(messages)
    print(f"\n最终上下文大小：{final:,} tokens")
    print("任务越复杂，这个数字越大，直到超出模型上限……\n")


def demo_multi_agent() -> None:
    """演示多 Agent 分工后，每个 Agent 的上下文保持在低位。"""
    print("=== 场景二：三个 Agent 各干各的 ===\n")

    # Researcher：只有自己的小任务
    researcher_msgs = [
        system("你是研究员，只负责整理主题核心要点。输出简洁要点列表，不超过150字。"),
        user("主题：人工智能"),
    ]
    research = chat(researcher_msgs, temperature=0.3)
    print(f"[Researcher] 上下文: {estimate_tokens(researcher_msgs):,} tokens")
    print(f"  输出（节选）：{research[:80]}...\n")

    # Writer：只看研究报告，看不到研究的来回过程
    writer_msgs = [
        system("你是写作者，根据研究报告写一段约200字的科普段落，直接输出文章内容。"),
        user(f"研究报告：\n{research}"),
    ]
    draft = chat(writer_msgs, temperature=0.8)
    print(f"[Writer]     上下文: {estimate_tokens(writer_msgs):,} tokens")
    print(f"  输出（节选）：{draft[:80]}...\n")

    # Editor：只看草稿，不知道前面发生了什么
    editor_msgs = [
        system("你是编辑，审核文章并给出一条最重要的改进建议，直接输出建议。"),
        user(f"文章草稿：\n{draft}"),
    ]
    feedback = chat(editor_msgs, temperature=0.4)
    print(f"[Editor]     上下文: {estimate_tokens(editor_msgs):,} tokens")
    print(f"  改进建议：{feedback[:80]}...\n")

    total = (estimate_tokens(researcher_msgs) +
             estimate_tokens(writer_msgs) +
             estimate_tokens(editor_msgs))
    print(f"三个 Agent 上下文合计：{total:,} tokens")
    print("每个 Agent 只关注自己的部分，专注度更高，上下文也更小。")


if __name__ == "__main__":
    demo_single_agent()
    print()
    demo_multi_agent()
