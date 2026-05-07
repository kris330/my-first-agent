from agent_loop import ReactAgent
from planner import make_plan, print_plan
from executor import execute_plan


def main() -> None:
    print("=== Day 6 Agent：规划 + 执行 ===")
    print("命令：")
    print("  直接输入        → ReAct 对话模式")
    print("  /plan <任务>   → 规划并执行复杂任务")
    print("  quit           → 退出\n")

    agent = ReactAgent(max_steps=5)

    while True:
        user_input = input("你：").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "/quit"):
            print("再见！")
            break

        if user_input.startswith("/plan "):
            task = user_input[6:].strip()
            if not task:
                print("用法：/plan 你的任务描述\n")
                continue

            print("\n正在制定计划...")
            plan = make_plan(task)
            print_plan(plan)

            confirm = input("\n确认执行？(y/n)：").strip().lower()
            if confirm == "y":
                result = execute_plan(plan)
                print(f"\nAgent：{result}\n")
            else:
                print("已取消。\n")
            continue

        # 普通 ReAct 对话
        result = agent.run(user_input)
        print(f"\nAgent：{result}\n")


if __name__ == "__main__":
    main()
