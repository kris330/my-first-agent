# Day 3：多工具 Agent，让它自己选

## 今天学什么

今天新增两个工具：**计算器** 和 **查当前时间**。

Agent 同时拥有4个工具，面对不同问题能自动选对工具。

这一天的核心不是工具本身，而是**工具注册表的设计**：
以后想加新工具，只需要在 `tool_registry.py` 里加几行，Agent 就自动学会用了。

## 今天的成果

```
你：现在几点了？
[AI 决策]: {"action": "use_tool", "tool": "get_current_time", "params": {"timezone": "Asia/Shanghai"}}
Agent：2024年03月15日 14:30:22（Asia/Shanghai）

你：(123 + 456) * 2 等于多少？
[AI 决策]: {"action": "use_tool", "tool": "calculate", "params": {"expression": "(123 + 456) * 2"}}
Agent：(123 + 456) * 2 = 1158

你：上海今天天气怎么样？
[AI 决策]: {"action": "use_tool", "tool": "get_weather", "params": {"city": "上海"}}
Agent：多云，18°C，南风2级
```

## 运行方法

```bash
cd day3
python main.py
```

## 新增工具说明

| 工具 | 文件 | 功能 |
|------|------|------|
| `calculate` | `tools/calculator.py` | 计算数学表达式 |
| `get_current_time` | `tools/datetime_tool.py` | 获取当前时间 |

## 如何自己加一个新工具

1. 在 `tools/` 目录下新建一个 `.py` 文件，写一个函数
2. 在 `tool_registry.py` 里的 `TOOLS` 字典里加一条记录
3. 搞定。Agent 下次运行就会自动知道这个工具的存在

## 常见问题

**Q：AI 选错工具了怎么办？**

A：在 `tool_registry.py` 里把工具描述写得更清晰，特别是"什么时候用"和"什么时候不用"。
例如：`"适合查找... 不适合用于计算类问题"`。

## 下一步

去 `day4/`，给 Agent 装上记忆，让它记住对话历史。
