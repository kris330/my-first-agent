"""
进阶 Day 2 演示：Orchestrator 调度员模式

Orchestrator 只负责调度，不处理业务逻辑。
Workers 只负责自己的专项任务，互不知晓。

运行：
  cd multi_agent
  python adv2_orchestrator.py
"""
from __future__ import annotations

import json

from llm import chat, system, user


# ── Workers（专项工人）─────────────────────────────────────────

class TranslatorWorker:
    """只负责翻译，不管任务全局。"""

    def run(self, text: str, target_lang: str = "英文") -> str:
        messages = [
            system("你是专业翻译，只输出翻译结果，不加任何说明。"),
            user(f"将下面的内容翻译成{target_lang}：\n{text}"),
        ]
        return chat(messages, temperature=0.2)


class SummarizerWorker:
    """只负责生成摘要。"""

    def run(self, text: str, max_sentences: int = 3) -> str:
        messages = [
            system(f"你是摘要专家，用不超过{max_sentences}句话概括核心内容，直接输出摘要。"),
            user(text),
        ]
        return chat(messages, temperature=0.3)


class SentimentWorker:
    """只负责情感分析。"""

    def run(self, text: str) -> str:
        messages = [
            system('分析文本情感，只输出 JSON：{"sentiment": "正面/负面/中性", "score": 0到1的数字, "reason": "一句话原因"}'),
            user(text),
        ]
        return chat(messages, temperature=0.1)


# ── Orchestrator（调度员）────────────────────────────────────

class SimpleOrchestrator:
    """
    调度员：解析用户意图，决定调用哪些 Worker、用什么顺序。
    自己不处理任何翻译、摘要、情感分析——那些都交给 Worker。
    """

    def __init__(self) -> None:
        self._workers: dict = {
            "translator": TranslatorWorker(),
            "summarizer": SummarizerWorker(),
            "sentiment": SentimentWorker(),
        }

    def _plan_tasks(self, request: str) -> list[dict]:
        """让 LLM 理解用户意图，规划需要调用哪些 Worker。"""
        messages = [
            system("""你是任务规划器，根据用户请求输出需要执行的任务列表（JSON 格式）。

可用的 worker：
- translator: 翻译文本，参数 target_lang（目标语言，默认"英文"）
- summarizer: 生成摘要，参数 max_sentences（句数，默认3）
- sentiment: 情感分析，无参数

输出格式（只输出 JSON 数组，不要任何说明文字）：
[{"worker": "名称", "params": {}, "use_prev": true/false}]

use_prev=true 表示这一步的输入是上一步的输出，false 表示用原始文本。
"""),
            user(request),
        ]
        raw = chat(messages, temperature=0.1)
        try:
            start = raw.index("[")
            end = raw.rindex("]") + 1
            return json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError):
            return []

    def run(self, request: str, text: str) -> dict[str, str]:
        print(f"\n[Orchestrator] 收到请求：{request}")
        tasks = self._plan_tasks(request)
        if not tasks:
            return {"error": "无法理解请求"}

        worker_names = [t["worker"] for t in tasks]
        print(f"[Orchestrator] 任务计划：{worker_names}")

        results: dict[str, str] = {}
        prev_output = text

        for task in tasks:
            name = task["worker"]
            params = task.get("params", {})
            input_text = prev_output if task.get("use_prev") else text

            worker = self._workers.get(name)
            if not worker:
                results[name] = f"未知 worker: {name}"
                continue

            print(f"  → 调用 {name}({params})")
            output = worker.run(input_text, **params)
            results[name] = output
            prev_output = output

        return results


if __name__ == "__main__":
    orch = SimpleOrchestrator()
    text = "今天发布了重大更新：新功能让用户可以一键自动化重复性工作，大幅提升效率，用户反馈非常积极。"

    test_cases = [
        "把这段话翻译成英文",
        "用2句话总结这段话",
        "分析这段话的情感",
        "先翻译成英文，再分析英文版的情感",
    ]

    for req in test_cases:
        print(f"\n{'='*55}")
        result = orch.run(req, text)
        for worker_name, output in result.items():
            print(f"\n[{worker_name} 结果]\n{output}")
