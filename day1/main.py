from agent import run_agent
from actions import execute_action


def main() -> None:
    print("=== 我的第一个 Agent ===")
    print("输入 quit 退出\n")

    while True:
        user_input = input("你：").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "/quit"):
            print("再见！")
            break

        # Step 1：让 AI 决策
        ai_response = run_agent(user_input)

        # Step 2：执行 AI 的决定
        result = execute_action(ai_response)

        print(f"Agent：{result}\n")


if __name__ == "__main__":
    main()
