from agent_loop import ReactAgent


def main() -> None:
    print("=== Day 5 Agent：ReAct 多步推理 ===")
    print("现在可以用多步骤完成复杂任务了！")
    print("输入 quit 退出\n")

    agent = ReactAgent(max_steps=5)

    while True:
        user_input = input("你：").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "/quit"):
            print("再见！")
            break

        result = agent.run(user_input)
        print(f"\nAgent：{result}\n")


if __name__ == "__main__":
    main()
