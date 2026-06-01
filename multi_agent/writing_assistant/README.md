# 多 Agent 写作助手

进阶篇最终项目：Researcher + Writer + Editor 三个 Agent 协作写文章。

## 快速开始

1. 在项目根目录配置 `.env`（或设置环境变量）：
   ```
   OPENAI_API_KEY=你的key
   # 国内用户：
   # OPENAI_BASE_URL=https://api.deepseek.com
   # OPENAI_MODEL=deepseek-chat
   ```

2. 安装依赖（如果还没装过）：
   ```bash
   pip install openai python-dotenv
   ```

3. 运行：
   ```bash
   cd multi_agent/writing_assistant
   python main.py "帮我写一篇关于人工智能的科普文章"
   ```

   也可以不带参数，进入交互式输入：
   ```bash
   python main.py
   ```

## 架构

用到了进阶篇的全部核心概念：

| 概念 | 对应进阶篇文章 |
|------|--------------|
| Orchestrator + Worker | 进阶 Day 2 |
| Task / TaskResult 协议 | 进阶 Day 3 |
| 错误处理 + 重试 | 进阶 Day 5 |

流水线：

```
用户输入
   ↓
[Orchestrator]  ← 调度、传递上下文、重试
   ↓         ↑ research_output
[Researcher]    → 分析主题，整理关键要点
   ↓         ↑ draft
[Writer]        → 根据研究报告写文章初稿
   ↓         ↑ 终稿
[Editor]        → 审核初稿，输出改进建议 + 终稿
   ↓
最终文章
```

## 文件说明

```
writing_assistant/
├── main.py           # 入口，命令行参数或交互式输入
├── protocol.py       # Task / TaskResult 协议定义
├── llm.py            # LLM 封装（独立，不依赖父目录）
└── agents/
    ├── orchestrator.py  # 调度员，驱动流水线 + 重试逻辑
    ├── researcher.py    # 研究员 Agent
    ├── writer.py        # 写作 Agent
    └── editor.py        # 编辑 Agent
```
