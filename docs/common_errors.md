# 常见错误汇总

遇到问题先来这里找，90% 的错误都在这里。

---

## 1. `KeyError: 'OPENAI_API_KEY'`

**原因：** 没有创建 `.env` 文件，或者 API Key 没有填入。

**解决：**
```bash
cp .env.example .env
# 用文本编辑器打开 .env，填入你的 API Key
```

---

## 2. `AuthenticationError: Incorrect API key`

**原因：** API Key 填错了，或者有多余的空格。

**解决：**
- 检查 `.env` 文件，Key 前后不能有空格
- 格式应该是：`OPENAI_API_KEY=sk-xxx`（等号两边没有空格）

---

## 3. `json.decoder.JSONDecodeError`

**原因：** AI 没有按要求返回纯 JSON，在 JSON 前后加了多余的文字。

**解决：**
- 代码里已经有 `safe_parse_json` 兜底函数
- 如果还是出错，在调用处加打印：`print(f"[AI原始回复]: {response}")`，看看 AI 到底返回了什么

---

## 4. `requests.exceptions.Timeout`

**原因：** 搜索工具网络超时（DuckDuckGo 在国内有时较慢）。

**解决：**
- 代码里已经设置了 `timeout=10`，超时会返回提示信息
- 如果网络较差，可以把 `timeout` 改大：`timeout=30`

---

## 5. `ModuleNotFoundError: No module named 'openai'`

**原因：** 依赖没有安装。

**解决：**
```bash
pip install -r requirements.txt
```

---

## 6. `RateLimitError: You exceeded your current quota`

**原因：** API 账户余额不足。

**解决：**
- 充值 OpenAI 账户
- 或者切换到国内 API（DeepSeek 等），修改 `llm.py` 里的 `base_url`

---

## 7. Agent 陷入死循环，一直在调用工具

**原因：** `agent_loop.py` 里有 `max_steps` 上限控制，正常情况不会死循环。

**解决：**
- 检查 `max_steps` 是否被意外修改
- 如果手动修改了 prompt，确保包含"给出 final_answer"的指令

---

## 8. 国内 API 怎么配置

修改 `llm.py`（或每个 day 里的 `llm.py`）：

```python
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://api.deepseek.com"  # DeepSeek
    # base_url="https://api.moonshot.cn/v1"  # 月之暗面
    # base_url="https://open.bigmodel.cn/api/paas/v4"  # 智谱
)
```

同时修改模型名：
```python
model="deepseek-chat"  # DeepSeek
# model="moonshot-v1-8k"  # 月之暗面
# model="glm-4"  # 智谱
```

---

## 9. Python 版本问题

本项目需要 **Python 3.10 或以上版本**（因为使用了 `str | None` 类型注解语法）。

检查版本：
```bash
python --version
```

---

## 10. `AttributeError: 'NoneType' object has no attribute ...`

**原因：** 工具返回了 `None`，但代码期望收到字符串。

**解决：**
工具函数确保总是返回字符串，不返回 `None`。检查 `tools/` 目录下对应工具的返回值。
