# Day 2：给 Agent 装上第一个真实工具

## 今天学什么

昨天的 Agent 用的是假天气数据。今天两件事：

1. **接入真实搜索工具**（DuckDuckGo，免费，不需要 Key）
2. **建立工具注册表**，为以后加更多工具打好基础

## 今天的成果

Agent 能真正上网搜索，返回真实信息。

```
你：最近有什么 AI 新闻？
[AI 决策]: {"action": "use_tool", "tool": "web_search", "params": {"query": "AI 人工智能最新新闻"}}
[执行工具]: web_search，参数：{'query': 'AI 人工智能最新新闻'}
[工具结果]: 摘要：...
Agent：根据搜索结果...
```

## 运行方法

```bash
cd day2
python main.py
```

## 新增文件说明

| 文件 | 作用 |
|------|------|
| `tools/search.py` | DuckDuckGo 搜索工具 |
| `tools/weather.py` | 天气工具（沿用 mock） |
| `tool_registry.py` | 工具注册中心（今天的核心） |
| `agent.py` | 升级版，通过注册表选工具 |

## 今天最重要的概念：工具描述

AI 不知道你有什么工具。你要**用文字告诉它**，它才能选择。

`tool_registry.py` 里的 `get_tools_description()` 函数，
会把所有工具的名字、用途、参数拼成一段文字，注入到 System Prompt 里。

AI 读了这段说明，就知道"哦，我有 `web_search` 工具可以用"。

这就是工具调用的本质：**靠 Prompt 里的说明书**。

## 常见问题

**Q：搜索结果为空怎么办？**

A：DuckDuckGo 对部分中文关键词覆盖有限。试试换英文关键词，或者换更具体的词。

**Q：搜索超时了？**

A：网络问题，`search.py` 已设置 `timeout=10`，超时会返回提示而不是崩溃。

## 下一步

去 `day3/`，给 Agent 同时装上搜索、计算、查时间三个工具，让它自己选。
