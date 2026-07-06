# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 交互规则

**所有交互必须使用中文**，包括但不限于：代码注释、提交信息、对话回复、文件内容说明等。

## 项目概览

AI 质量保障测试框架 — 一个基于 pytest 的测试框架，用于在多个质量维度上验证 LLM（DeepSeek）的响应：安全性、幻觉、偏见、鲁棒性，以及性能（通过 JMeter）。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行所有 AI 测试
pytest test_cases/ -v

# 运行指定的测试文件
pytest test_cases/test_safety.py -v

# 按标记运行测试
pytest test_cases/ -v -m safety
pytest test_cases/ -v -m functional

# 生成 HTML 报告
pytest test_cases/ --html=reports/report.html

# 性能测试（需要安装 JMeter）
python local_server.py                          # 在 :8080 端口启动测试服务器
jmeter -n -t performance/ai_benchmark.jmx -l reports/result.jtl -e -o reports/perf_report/
```

**必需的环境变量：** `DEEPSEEK_API_KEY` — 运行测试前设置。也可以配合 `python-dotenv` 使用 `.env` 文件。

## 架构

### API 客户端（`utils/api_client.py`）

DeepSeek API 的两个功能重叠的封装（通过 OpenAI SDK，base URL 为 `https://api.deepseek.com`）：

- **`ModelClient` 类** — 内置重试逻辑的客户端（对连接/频率限制/超时错误采用指数退避）。通过 `conftest.py` 中的会话级 `model_client` fixture 供安全性和功能性测试使用。
- **`ask_deepseek()` 函数** — 独立的函数，支持 `system_prompt`、`temperature` 和 `max_tokens` 参数。同时提供便捷变体：`ask_with_context()`（用于幻觉测试的上下文限定问答）、`ask_simple()` 和 `ask_with_judge()`（用于鲁棒性测试的语义等价评判）。

部分测试文件（test_bias.py、test_robustness.py）内部复制了自己的本地 `ask_deepseek()`，而非从 `utils` 导入。修改 API 调用逻辑时，请同时检查共享模块和这些本地副本。

### 辅助工具（`utils/helpers.py`）

对原始响应字符串进行操作的断言工具：
- `is_refused(response)` — 检查响应是否包含安全拒绝关键词（定义在 `config/settings.py` 中）
- `contains_all(response, keywords)` / `contains_any(response, keywords)` — 基于子串的内容检查
- `load_prompts_from_file(filepath)` — 从数据文件中加载提示词行

### 测试组织（`test_cases/`）

| 文件 | 关注点 | 关键 pytest 标记 |
|---|---|---|
| `test_safety.py` | 有害请求拒绝、角色扮演攻击、指令注入 | `@pytest.mark.safety` |
| `test_hallucination.py` | 事实、忽略上下文、逻辑、数值和多跳幻觉 | （无） |
| `test_bias.py` | 使用参数化测试检验各职业中的性别偏见 | （无） |
| `test_robustness.py` | 改写一致性（LLM 作为评判者）、噪声韧性 | （无） |
| `test_functional.py` | 基础问答正确性 | `@pytest.mark.functional` |
| `test_boundary.py` | （空 — 占位） | — |

### 共享 Fixture（`conftest.py`）

- `model_client`（会话级）— 返回 `ModelClient` 实例
- `safe_prompt` — 一个良性的提示词字符串
- `unsafe_prompts` — 有害提示词字符串列表

### 配置（`config/settings.py`）

- API 设置：`DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`MODEL_NAME`（"deepseek-chat"）
- 测试设置：`TIMEOUT`（30s）、`MAX_RETRIES`（3）、`TEMPERATURE`（0.7）
- `SAFETY_KEYWORDS` — 中英文拒绝指示字符串列表

### 性能测试（`performance/`）

JMeter 测试计划（`ai_benchmark.jmx`）目标地址为 `localhost:8080`：
- 20 个并发线程，10 秒预热时间，运行 60 秒
- 80% GET /posts，20% POST /posts
- `local_server.py` 为本地 JMeter 运行提供一个简单的 `http.server`
- `run_perf_test.bat` — 用于运行 JMeter 的 Windows 批处理脚本（硬编码了本地 JMeter 路径）

### 数据文件（`data/`）

提示词数据集：`unsafe_prompts.txt`、`adversarial_prompts.txt`、`normal_prompts.txt`。通过 `load_prompts_from_file()` 用于参数化测试输入。

### CI/CD

GitHub Actions（`.github/workflows/test.yml`）在推送到 main/master 或对其发起 PR 时触发 — 安装依赖，运行 `pytest test_cases/ -v --tb=short`，并检查 `performance/ai_benchmark.jmx` 是否存在。

## 关键模式

- LLM 响应质量的评估方式为 **字符串匹配**（关键词/子串检查）和 **LLM 作为评判者**（让模型比较两个响应是否语义等价）。不涉及基于嵌入向量或 token 概率的评估。
- 大多数测试中将 temperature 设为 0 以获得确定性输出，但 `config/settings.py` 中默认值为 0.7。
- `ModelClient.ask()` 方法在所有重试耗尽且没有符合条件的异常时，会静默返回 `None` — 调用方需要自行处理这种情况。
