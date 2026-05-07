from config import load_config
from agent_loop import ReactAgent
from planner import make_plan, print_plan
from executor import execute_plan


BANNER = """
=================================================
    我的 AI Agent 系统 v1.0
=================================================
命令：
  直接输入     → 对话模式（有记忆，自动使用工具）
  /plan <任务> → 规划模式（先制定计划再执行）
  /clear       → 清除对话记忆，开始新对话
  /help        → 显示帮助
  /quit        → 退出
=================================================
"""

HELP_TEXT = """
命令说明：
  直接输入任何问题  → Agent 会判断是否用工具，有对话记忆
  /plan <任务描述>  → 先生成执行计划（你可以确认后再执行）
  /clear            → 清除对话记忆
  /help             → 显示本帮助

示例：
  你：北京今天天气怎样，适合跑步吗？
  你：帮我计算 (1234 + 5678) * 3
  你：/plan 帮我调研最近 AI 编程工具的发展动态，写一份简要报告
"""


def main() -> None:
    load_config()
    print(BANNER)

    agent = ReactAgent(max_steps=5)

    while True:
        try:
            user_input = input("你：").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

        if not user_input:
            continue

        # ── 退出 ──────────────────────────────
        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print("再见！")
            break

        # ── 帮助 ──────────────────────────────
        if user_input.lower() == "/help":
            print(HELP_TEXT)
            continue

        # ── 清除记忆 ──────────────────────────
        if user_input.lower() == "/clear":
            agent.clear_memory()
            print("记忆已清除，开始新对话。\n")
            continue

        # ── 规划模式 ──────────────────────────
        if user_input.lower().startswith("/plan "):
            task = user_input[6:].strip()
            if not task:
                print("用法：/plan 你的任务描述\n")
                continue

            print("\n正在制定计划...")
            plan = make_plan(task)
            print_plan(plan)

            try:
                confirm = input("\n确认执行？(y/n)：").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\n已取消。\n")
                continue

            if confirm == "y":
                result = execute_plan(plan)
                print(f"\nAgent：{result}\n")
            else:
                print("已取消。\n")
            continue

        # ── 普通对话（ReAct 模式） ─────────────
        result = agent.run(user_input)
        print(f"\nAgent：{result}")
        print(f"（对话记忆：{agent.memory_count()} 条）\n")


if __name__ == "__main__":
    main()
