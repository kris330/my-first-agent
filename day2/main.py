from agent import run_agent


def main() -> None:
    print("=== Day 2 Agent：带真实工具 ===")
    print("现在可以真正搜索互联网了！")
    print("输入 quit 退出\n")

    while True:
        user_input = input("你：").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "/quit"):
            print("再见！")
            break

        result = run_agent(user_input)
        print(f"Agent：{result}\n")


if __name__ == "__main__":
    main()
