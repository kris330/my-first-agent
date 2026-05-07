# Day 4：给 Agent 装上记忆

## 今天学什么

AI 天生失忆。每次调用 API，对它来说都是全新的对话。

今天解决这个问题：**把对话历史带进每次 API 请求**，让 Agent 记住你说过的话。

## 今天的成果

```
你：我叫小明，我在学习 Python
Agent：你好小明！很高兴认识你。Python 是一门很棒的语言...

你：我刚才说我叫什么名字？
Agent：你说你叫小明，并且正在学习 Python。

你：/clear
记忆已清除，开始新对话。

你：我叫什么名字？
Agent：我不知道您的名字，您还没有告诉过我。
```

## 运行方法

```bash
cd day4
python main.py
```

## 新增文件

| 文件 | 作用 |
|------|------|
| `memory/short_term.py` | 短期记忆，保存对话历史，控制上限 |
| `agent.py` | 重构成 `Agent` 类，把记忆集成进去 |

## 记忆的工作原理

```
第1轮：
  发送给 API：[system, user("我叫小明")]
  API 返回：assistant("你好小明！")

第2轮：
  发送给 API：[system, user("我叫小明"), assistant("你好小明！"), user("我叫什么？")]
                ↑ 把历史都带上了！
  API 返回：assistant("你叫小明。")
```

记忆的本质就是：**把历史消息拼在新消息前面，一起发给 API**。

## 为什么要有 max_messages 上限

每条消息都要占用 token。如果对话很长，token 会超出模型上限，API 会报错。

`ShortTermMemory` 设置了 `max_messages=20`，超过就自动删掉最旧的消息。

## 下一步

去 `day5/`，给 Agent 加上 ReAct 循环，让它能多步骤自动完成任务。
