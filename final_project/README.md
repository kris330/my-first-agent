# Final Project：完整 AI Agent 系统

这是7天课程的最终成果，包含全部能力的完整项目。

## 运行方法

```bash
# 确保已在项目根目录配置好 .env
cd final_project
python main.py
```

## 能力清单

| 能力 | 实现文件 | 说明 |
|------|----------|------|
| AI 对话 | `llm.py` | 封装 API 调用，支持国内服务 |
| 工具调用 | `tool_registry.py` | 4个内置工具，可自由扩展 |
| 短期记忆 | `memory/short_term.py` | 保留最近20条，自动截断 |
| ReAct 循环 | `agent_loop.py` | 多步推理，最多5步 |
| 任务规划 | `planner.py` | 生成3-6步执行计划 |
| 计划执行 | `executor.py` | 按步骤执行并整合答案 |
| 配置管理 | `config.py` | .env 加载，启动检查 |

## 内置工具

| 工具 | 用途 |
|------|------|
| `web_search` | 搜索互联网（DuckDuckGo，免费） |
| `get_weather` | 查询城市天气 |
| `calculate` | 计算数学表达式 |
| `get_current_time` | 获取当前时间 |

## 如何添加新工具

1. 在 `tools/` 目录下新建 `.py` 文件，写一个函数
2. 在 `tool_registry.py` 的 `TOOLS` 字典里加一条记录（名称、描述、参数）
3. 完成，Agent 下次运行自动学会这个工具

## 环境变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `OPENAI_API_KEY` | 是 | API Key |
| `OPENAI_BASE_URL` | 否 | 国内 API 地址，不设则用 OpenAI 官方 |
| `OPENAI_MODEL` | 否 | 模型名，默认 `gpt-4o-mini` |

## 国内 API 配置示例

在 `.env` 里：
```
OPENAI_API_KEY=你的key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```
