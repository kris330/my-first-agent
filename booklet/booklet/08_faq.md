# 《7天手搓 Agent》读者常见问题汇总

> 系列番外 · 持续更新

---
大家好，欢迎来到小撒的私房菜，我是小撒。

这篇文章收录系列发布以来读者最常问的问题。

分三类：**环境和配置**、**代码运行**、**理解和扩展**。

---

## 一、环境和配置类

---

**Q：国内用什么 API 替代 OpenAI？**

几个主流选择：

| 服务 | 特点 | 注册地址 |
|---|---|---|
| DeepSeek | 效果接近 GPT-4，价格极低，推荐 | platform.deepseek.com |
| 月之暗面（Moonshot） | 支持超长上下文 | platform.moonshot.cn |
| 智谱 AI（GLM） | 国内老牌，文档完善 | open.bigmodel.cn |
| 阿里通义 | 生态完整 | dashscope.aliyun.com |

所有这些都支持 OpenAI 兼容接口，只需要改 `base_url` 和模型名，其他代码一行不动。

修改方式，在 `.env` 里：
```
OPENAI_API_KEY=你的key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

---

**Q：用 `gpt-4o-mini` 还是 `gpt-4o`？**

跑这个系列，`gpt-4o-mini` 完全够用，而且便宜很多（约便宜15倍）。

`gpt-4o` 或 `gpt-4o-mini` 的区别主要在复杂推理任务上。对于工具调用、简单对话，mini 版本表现很好。

建议：开发和学习用 mini，有具体的效果不满意了再换大模型。

---

**Q：`.env` 文件怎么创建？在 Windows 上怎么弄？**

`.env` 是一个普通文本文件，文件名就叫 `.env`（没有扩展名，以点开头）。

**macOS / Linux：**
```bash
cp .env.example .env
# 然后用任何文本编辑器打开编辑
```

**Windows：**

方法1：在终端里
```cmd
copy .env.example .env
notepad .env
```

方法2：直接在 VS Code 里右键 `.env.example` → 复制 → 粘贴 → 重命名为 `.env` → 编辑

注意：Windows 文件资源管理器可能不显示以点开头的文件，要在"查看"里开启"显示隐藏文件"。

---

**Q：`pip install` 速度太慢怎么办？**

换国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

或者一次性配置永久生效：

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

**Q：Python 版本不够怎么升级？**

本系列需要 Python 3.10+，因为用了 `str | None` 这种联合类型语法。

**macOS：**
```bash
brew install python@3.12
```

**Windows：**
去 python.org 下载最新安装包，选"Add to PATH"安装。

---

## 二、代码运行类

---

**Q：`json.decoder.JSONDecodeError` 一直出现怎么办？**

这是最常见的问题，原因是 AI 没有老老实实返回纯 JSON。

**诊断步骤：**

1. 在调用 AI 之后立刻加一行打印：
```python
print(f"[AI 原始回复]: {repr(response)}")
```

2. 看看 AI 到底返回了什么，常见情况：
   - 在 JSON 前面加了 "好的，" / "当然，" 等前缀
   - 用了 Markdown 代码块包裹：` ```json {...} ``` `
   - 返回了中文解释而不是 JSON

**解决方法：**

代码里已经有 `safe_parse_json()` 函数，大多数情况能兜住。

如果还是出问题，在 System Prompt 里加强约束：
```
你的回复必须且只能是一个 JSON 对象。
不要在 JSON 前后添加任何文字。
不要使用 Markdown 代码块。
直接输出 JSON，从 { 开始，到 } 结束。
```

---

**Q：搜索工具一直返回空结果或出错怎么办？**

DuckDuckGo 对中文关键词的覆盖有限，可以：

1. 换成英文关键词试试
2. 换个具体的关键词（"Python 3.12 新特性" 比 "Python" 效果好）

如果想用效果更好的搜索，可以考虑替换成：
- **Tavily Search API**（专为 AI Agent 设计，有免费额度）
- **Serper API**（Google 搜索结果，有免费额度）
- **Bing Search API**（微软，有免费额度）

替换方式：把 `tools/search.py` 里的实现换掉，注册表不需要改。

---

**Q：Agent 陷入死循环，一直在调用工具不停止**

检查 `agent_loop.py` 里的 `max_steps` 参数，确保它是一个正整数（默认是5）。

如果 `max_steps` 正常，可能是 System Prompt 里没有说清楚"达到信息就给出 final_answer"，加上这句：

```
一旦你收集到足够的信息来回答用户问题，立即给出 final_answer，不要继续搜索。
```

---

**Q：运行到一半报 `RateLimitError` 怎么办？**

这是 API 调用频率超限或余额不足。

- **余额不足**：充值
- **调用太频繁**：在每次 API 调用前加 `time.sleep(1)` 降低频率
- **DeepSeek 等国内 API**：额度限制通常更宽松

---

**Q：Day4 之后，工具调用结果有时候不准确，AI 好像没有基于工具结果回答**

这是因为 Day4 的代码里，工具结果存入记忆后，会**再调用一次 API** 让 AI 基于结果给出自然语言答案。

如果第二次 API 调用的 prompt 不够清晰，AI 可能给出通用答案而不是基于工具结果的答案。

检查这段代码：
```python
self.memory.add("user",
    f"[工具 {tool_name} 返回结果]：{tool_result}\n"
    f"请基于此结果，用自然语言回答用户的问题。"
)
```

如果效果不好，可以把最后一句改得更具体：
```
"请直接引用工具返回的数据，给出具体的回答，不要说'根据搜索结果'这类模糊表述。"
```

---

## 三、理解和扩展类

---

**Q：为什么用 Prompt 约束 AI 返回 JSON，而不用约束解码？这样可靠吗？**

这是个很好的问题，值得把两种方案说清楚。

**文章用的方案——"软约束"：**

在 System Prompt 里告诉 AI "只返回 JSON"，再配合 `safe_parse_json()` 用正则兜底。
优点是简单、跨模型通用，对 DeepSeek、月之暗面等所有兼容 OpenAI 格式的 API 一行不改就能用。
缺点是不保证 100%：极少数情况下 AI 会忽略指令，返回完全无法解析的内容。

**更可靠的方案——"硬约束"（约束解码）：**

在 token 生成阶段直接过滤掉不合法的输出，从机制上保证结果是合法 JSON。有两类实现方式：

| 场景 | 方案 |
|---|---|
| OpenAI / DeepSeek API | `response_format={"type": "json_schema", "json_schema": {...}}` （Structured Outputs） |
| 本地模型 | `outlines`、`guidance`、`lm-format-enforcer` 等库 |

**什么时候该升级：**

- 学习阶段：Prompt 软约束 + `safe_parse_json()` 够用，先跑通逻辑
- 生产环境 / 对可靠性有要求：用 API 层的 Structured Outputs，不依赖 Prompt，模型也专门为此优化过

升级到 OpenAI Structured Outputs 的改动很小，只需要在 `chat()` 调用里加一个参数：

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "agent_decision",
            "schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "city":   {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["action"],
            }
        }
    }
)
```

理解了 Prompt 软约束的原理之后，再迁移到硬约束会很自然——两者做的事情一样，只是保障层次不同。

---

**Q：这个 Agent 和 ChatGPT 有什么区别？**

ChatGPT 是一个对话产品，封装了记忆、工具调用（搜索、画图等）、系统提示等功能。

你做的 Agent 和它的底层逻辑是一样的：
- 记忆 = 把历史消息带进请求
- 工具调用 = AI 返回工具名和参数，程序执行
- 多步完成任务 = ReAct 循环

区别在于：ChatGPT 是成品，你做的是你完全理解和控制的版本。

---

**Q：这个和 LangChain 是什么关系？**

你手搓的这套东西，LangChain 几乎都有对应的封装：

| 你的代码 | LangChain 对应 |
|---|---|
| `tool_registry.py` | `Tool` / `StructuredTool` |
| `memory/short_term.py` | `ConversationBufferMemory` |
| `agent_loop.py` (ReactAgent) | `AgentExecutor` |
| `planner.py` + `executor.py` | `Plan-and-Execute` chain |
| `llm.py` | `ChatOpenAI` |

学完这个系列再去看 LangChain，你会发现自己已经理解了它的核心概念，只是换了个 API 而已。

---

**Q：现在 OpenAI 有官方的 Function Calling，和我们手搓的有什么区别？**

OpenAI 的 Function Calling（现在叫 Tool Calling）是 API 层面的官方支持，让 AI 返回结构化的工具调用，不需要靠 Prompt 约束格式。

我们手搓的是用 System Prompt 让 AI 返回 JSON 来模拟工具调用，本质上做到了同样的事。

官方 Function Calling 的优势：
- 更稳定（不依赖 Prompt）
- 模型专门为此微调过，选工具更准确
- 支持并行工具调用

学完这个系列，迁移到官方 Function Calling 非常容易，原理是一样的，只是调用 API 的参数变了。

---

**Q：怎么让 Agent 读写本地文件？**

新建 `tools/file_tool.py`：

```python
def read_file(path: str) -> str:
    """读取文件内容。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"文件不存在：{path}"
    except Exception as e:
        return f"读取出错：{e}"


def write_file(path: str, content: str) -> str:
    """写入文件内容。"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"已写入文件：{path}"
    except Exception as e:
        return f"写入出错：{e}"
```

然后在 `tool_registry.py` 里注册。搞定。

---

**Q：系列完结了，有进阶内容推荐吗？**

**下一步读物：**
- ReAct 论文（2022）：理解 Agent 循环的理论基础
- LangChain 官方文档：看现在你能读懂多少
- OpenAI Cookbook：大量实用示例

**下一步实践：**
1. 给 Agent 加一个你自己最需要的工具
2. 做一个有 Web 界面的版本（试试 Gradio，十分钟搞定）
3. 把记忆持久化到文件（JSON 格式就行）
4. 尝试实现一个简单的 Multi-Agent：一个规划，一个执行

---

*本文持续更新，如果你遇到了新问题，欢迎评论区留言。*

*如果这个系列对你有帮助，分享给需要的朋友是对我最大的支持。*

如果本教程对你有所帮助，留下一个免费的三连吧，这是对我最大的鼓励♥️！