# 从零搭建你的第一个 AI Agent

> 7天，用最简单的 Python，做一个真正能运行的 AI Agent 系统。

不用 LangChain，不用 AutoGen，从最小 Agent 开始，一步步生长。

---

## 最终效果

运行 `final_project/main.py` 后，你会得到一个支持多工具、有记忆、能多步推理的 Agent：

```
=================================================
    我的 AI Agent 系统 v1.0
=================================================
命令：
  直接输入    → 对话模式（有记忆，自动使用工具）
  /plan <任务> → 规划模式（先制定计划再执行）
  /clear      → 清除对话记忆
  /quit       → 退出
=================================================

你：帮我搜索一下最近 AI 领域的新闻

[步骤 1/5]
[AI 思考]: {"type": "tool_call", "tool": "web_search", ...}
[调用工具]: web_search
[工具结果]: ...

Agent：根据最新搜索结果，以下是 AI 领域近期重要动态：...
```

---

## 快速开始（5分钟内跑通）

### 第一步：下载代码

```bash
git clone https://github.com/你的用户名/my-first-agent.git
cd my-first-agent
```

### 第二步：安装依赖

```bash
pip install -r requirements.txt
```

> 需要 Python 3.10 或以上版本。检查版本：`python --version`

### 第三步：配置 API Key

```bash
cp .env.example .env
```

用文本编辑器打开 `.env`，把 `sk-xxx` 替换成你的真实 Key。

### 第四步：运行第一个 Agent

```bash
cd day1
python main.py
```

看到 `=== 我的第一个 Agent ===` 就成功了。

---

## 7天学习路径

| 天数 | 学习内容 | 新增能力 | 目录 |
|------|----------|----------|------|
| Day 1 | 最小 Agent + 结构化决策 | 感知 → 思考 → 行动 | `day1/` |
| Day 2 | 真实工具调用 | 搜索互联网 | `day2/` |
| Day 3 | 多工具系统 | 自动选工具 | `day3/` |
| Day 4 | 短期记忆 | 多轮对话不失忆 | `day4/` |
| Day 5 | ReAct 循环 | 多步自动完成任务 | `day5/` |
| Day 6 | 任务规划 | 拆解复杂任务 | `day6/` |
| Day 7 | 完整整合 | 所有能力组合 | `final_project/` |

每个目录里有独立的 `README.md`，告诉你今天学什么、怎么运行。

---

## 需要什么基础

- Python 基础（变量、函数、if/else、for 循环）
- 一个 OpenAI API Key，或者任何兼容 OpenAI 格式的服务
- 不需要了解 LangChain / AutoGen / 任何 Agent 框架

---

## API Key 去哪里拿

**OpenAI 官方（推荐，效果最好）：**
- 注册：https://platform.openai.com
- 价格：gpt-4o-mini 非常便宜，跑完7天课程大约花 $0.5 以内

**国内替代方案（不需要梯子）：**
- DeepSeek：https://platform.deepseek.com（效果接近 GPT-4，价格极低）
- 月之暗面：https://platform.moonshot.cn
- 智谱 AI：https://open.bigmodel.cn

**如何切换到国内 API：**

修改每个 day 目录里的 `llm.py`（或 `final_project/llm.py`）：

```python
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://api.deepseek.com",  # 改这里
)

# chat 函数里的 model 也要改：
model="deepseek-chat"
```

在 `.env` 里填入对应平台的 Key 即可，其他代码不用动。

---

## 遇到问题

查看 [docs/common_errors.md](docs/common_errors.md)，收录了10种最常见的错误和解决方法。

---

## 项目结构

```
my-first-agent/
├── day1/            # Day 1：最小 Agent
├── day2/            # Day 2：真实工具
├── day3/            # Day 3：多工具
├── day4/            # Day 4：记忆
├── day5/            # Day 5：ReAct 循环
├── day6/            # Day 6：规划能力
├── day7/            # Day 7：指向 final_project
├── final_project/   # 最终完整项目
├── screenshots/     # 运行截图
├── docs/
│   └── common_errors.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 学完之后能做什么

这个课程结束后，你会真正理解 Agent 的工作原理，而不是只会用框架。

之后可以继续探索：
- 换成 LangChain / LlamaIndex（你会发现它们解决的正是你亲手遇到的问题）
- 给 Agent 加上更多工具（发邮件、操作文件、调用数据库）
- 做一个有 Web 界面的 Agent（用 FastAPI + 简单前端）
- 探索 Multi-Agent 系统（多个 Agent 协作）
