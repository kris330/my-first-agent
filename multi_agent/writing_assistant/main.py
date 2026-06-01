"""
多 Agent 写作助手 —— 入口文件

运行方式：
  python main.py "帮我写一篇关于量子计算的科普文章"
  python main.py        # 交互式输入
"""
from __future__ import annotations

import os
import sys

# 确保能找到同级模块（llm.py、protocol.py、agents/）
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from agents.orchestrator import OrchestratorAgent


def main() -> None:
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
    else:
        request = input("请输入写作需求（例如：写一篇关于 AI 的科普文章）：\n> ").strip()

    if not request:
        print("需求不能为空。")
        sys.exit(1)

    orchestrator = OrchestratorAgent()
    article = orchestrator.run(request)

    print("=" * 60)
    print(article)
    print("=" * 60)


if __name__ == "__main__":
    main()
