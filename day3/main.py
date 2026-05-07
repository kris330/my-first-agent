from agent import run_agent


def main() -> None:
    print("=== Day 3 Agent：多工具版 ===")
    print("工具：搜索 / 天气 / 计算 / 当前时间")
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
