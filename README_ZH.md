# 🧠 OntoMem: 自我整合的记忆系统

<div align="center">

[English](README.md)

</div>

**OntoMem** 构建于*本体记忆*（Ontology Memory）的概念之上——为 AI 系统提供结构化、连贯的知识表示。

> **让你的 AI 智能体拥有"连贯"的记忆，而不仅仅是"碎片"的检索。**

<p align="center">
  <img src="docs/assets/fw.png" alt="OntoMem Framework Diagram" width="800" />
</p>

<div align="center">

<a href="https://pypi.org/project/ontomem/"><img src="https://img.shields.io/pypi/v/ontomem.svg" alt="PyPI 版本"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"></a>
<a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
<a href="https://pypi.org/project/ontomem/"><img src="https://img.shields.io/pypi/dm/ontomem.svg" alt="PyPI 下载数"></a>
<a href="https://yifanfeng97.github.io/ontomem/"><img src="https://img.shields.io/badge/docs-latest-green" alt="Documentation"></a>
</div>


传统的 RAG（检索增强生成）系统检索文本碎片。**OntoMem** 采用 Pydantic 模式维护**结构化实体**，并通过智能合并算法自动将碎片化的观察融合为完整的知识图谱节点。

**它不仅仅存储数据——它持续"消化"和"组织"数据。**

## 📰 最新动态
<details>
<summary>详情</summary>

- **[2026-01-21] v0.1.5 发布**:
  - **🎯 生产环境安全**: 新增 `max_workers` 参数控制 LLM 批量处理并发数
  - **⚡ 防止 API 限流**: 有效防止触发 OpenAI 等 LLM 提供商的速率限制，避免账户被限制
  - **🔧 细粒度并发控制**: 按合并策略自定义并发工作线程数（默认值: 5）
  - [了解更多 →](docs/zh/user-guide/merge-strategies.md#控制-llm-并发)

- **[2026-01-19] v0.1.4 发布**:
  - **API 改进**: 将 `merge_strategy` 参数改名为 `strategy_or_merger`，更清晰且灵活
  - **增强功能**: 新增 `**kwargs` 支持，可直接通过 `OMem` 传入合并器特定参数（如 `CUSTOM_RULE` 的 `rule` 和 `dynamic_rule`），无需预配置
  - **优势**: 更简洁的 API 和更直观的高级合并使用方式
  - [了解更多 →](docs/zh/user-guide/merge-strategies.md)

- **[2026-01-19] v0.1.3 发布**:
  - **新特性**: 新增 `MergeStrategy.LLM.CUSTOM_RULE` 策略，支持用户自定义合并逻辑。直接向 LLM 合并器注入静态规则和动态上下文（通过函数）！
  - **破坏性变更**: 为提高清晰度，重命名了旧版策略名称：
    - `KEEP_OLD` → `KEEP_EXISTING`
    - `KEEP_NEW` → `KEEP_INCOMING`
    - `FIELD_MERGE` → `MERGE_FIELD`
  - [了解更多关于自定义规则](docs/zh/user-guide/merge-strategies.md#custom-rules)

</details>

## ✨ 为什么选择 OntoMem？

### 🧩 Schema-First（模式优先）& 类型安全
基于 **Pydantic** 构建。所有记忆都是强类型对象。告别 `{"unknown": "dict"}` 的地狱，拥抱 IDE 自动补全和类型检查。

### 🔄 自动整合（Auto-Consolidation）
当你多次插入关于同一实体（相同 ID）的不同信息时，OntoMem 不会创建重复记录。它使用可配置的策略（字段覆盖、列表合并或 **LLM 驱动的智能融合**）将其智能合并为一条**黄金记录**。

### 🔍 混合搜索（Hybrid Search）
- **键值查询**：O(1) 精确实体访问
- **向量搜索**：内置 FAISS 索引用于语义相似性搜索，自动同步

### 💾 状态保持 & 持久化
将完整的记忆状态（结构化数据 + 向量索引）保存到磁盘，下次启动时可在秒级恢复。


## 🧠 OntoMem 与其他记忆库对比

大多数记忆库存储的是**原始文本**或**聊天记录**。OntoMem 存储的是**经过整合的知识**。

| 特性 | **OntoMem** 🧠 | **Mem0** / Zep | **LangChain Memory** | **向量数据库** (Pinecone/Chroma) |
| :--- | :--- | :--- | :--- | :--- |
| **核心存储单元** | ✅ **结构化对象** (Pydantic) | 文本切片 + 元数据 | 原始对话日志 | 向量 Embeddings |
| **数据"消化"能力** | ✅ **自动整合与逻辑合并** | 简单抽取 | ❌ 仅追加 (Append-only) | ❌ 仅追加 |
| **时间维度感知** | ✅ **时序切片** (按日/会话聚合) | ❌ 仅时间戳元数据 | ❌ 仅线性顺序 | ❌ 仅元数据过滤 |
| **冲突解决机制** | ✅ **LLM 智能逻辑** (综合/取舍) | ❌ 最后写入优先 | ❌ 无 | ❌ 无 |
| **类型安全** | ✅ **严格 Schema 约束** | ⚠️ 松散 JSON | ❌ 仅字符串 | ❌ 无 |
| **适用场景** | **长期 Agent 画像、动态知识图谱** | 简单 RAG、搜索增强 | 聊天机器人上下文 | 语义搜索 |

### 💡 "自动整合"的优势

- **传统 RAG/Memory**: 存储 50 条零散记录（如"Alice 喜欢苹果"、"Alice 喜欢香蕉"）。检索时返回 50 个碎片。
- **OntoMem**: 将其"消化"为 1 个对象：`User(name="Alice", likes=["苹果", "香蕉"])`。检索时返回**唯一的完整事实**。


## 🚀 快速开始

30 秒内构建一个结构化的记忆存储。

### 1. 定义 & 初始化

```python
from pydantic import BaseModel
from ontomem import OMem
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 1. 定义你的记忆 schema
class UserProfile(BaseModel):
    name: str
    skills: list[str]
    last_seen: str

# 2. 初始化（含 LLM 合并和并发控制，v0.1.5+）
memory = OMem(
    memory_schema=UserProfile,
    key_extractor=lambda x: x.name,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    max_workers=3  # 🆕 控制 LLM 批量处理的并发数，防止 API 限流
)
```

### 2. 添加 & 合并（自动合并）

OntoMem 自动为相同 ID 的数据进行合并。

```python
# 第一条观察
memory.add(UserProfile(name="Alice", skills=["Python"], last_seen="10:00"))

# 之后的观察（新增了技能，时间更新）
memory.add(UserProfile(name="Alice", skills=["Docker"], last_seen="11:00"))

# 获取合并后的"黄金记录"
alice = memory.get("Alice")
print(alice.skills)     # ['Python', 'Docker']（列表已合并！）
print(alice.last_seen)  # "11:00"（已更新！）
```

### 3. 搜索 & 检索

```python
# 精确检索
profile = memory.get("Alice")

# 所有 key
all_keys = memory.keys

# 清空或删除
memory.remove("Alice")
```


## 💡 高级示例

<details>
<summary><b>示例 1：自我优化的调试智者（逻辑演进）</b></summary>

一个 AI 智能体不仅存储错误，还利用 `LLM.BALANCED` 策略随时间**合成**调试智慧。

```python
from ontomem import OMem, MergeStrategy
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class BugFixExperience(BaseModel):
    error_signature: str
    solutions: list[str]
    prevention_tips: str

memory = OMem(
    memory_schema=BugFixExperience,
    key_extractor=lambda x: x.error_signature,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.BALANCED
)

# 第一天：Pip 安装
memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: pandas",
    solutions=["pip install pandas"],
    prevention_tips="检查 requirements.txt"
))

# 第二天：Docker 容器（不同的解决方案！）
memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: pandas",
    solutions=["apt-get install python3-pandas"],  # 添加到列表！
    prevention_tips="在容器中使用系统包"  # LLM 合并两条提示
))

# 结果：单条记录，包含合并的解决方案 + 合成的建议
guidance = memory.get("ModuleNotFoundError: pandas")
print(guidance.prevention_tips)
# >>> "在标准环境中，检查 requirements.txt。
#      在容器化环境中，更倾向使用系统包..."
```

</details>

<details>
<summary><b>示例 2：时序记忆 & 日汇总（时间序列）</b></summary>

使用**组合键**将一系列碎片化事件转化为单条"日汇总"记录。

```python
from ontomem import OMem, MergeStrategy

class DailyTrace(BaseModel):
    user: str
    date: str
    actions: list[str]  # 累积整天的操作
    summary: str        # LLM 合成整天的概括

memory = OMem(
    memory_schema=DailyTrace,
    key_extractor=lambda x: f"{x.user}_{x.date}",  # <-- 神奇的键
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.BALANCED
)

# 上午 9:00 事件
memory.add(DailyTrace(user="Alice", date="2024-01-01", actions=["Login"]))

# 下午 5:00 事件（同一天 → 合并到相同记录）
memory.add(DailyTrace(user="Alice", date="2024-01-01", actions=["Logout"]))

# 第二天（新日期 → 新记录）
memory.add(DailyTrace(user="Alice", date="2024-01-02", actions=["Login"]))

# 结果：
# - alice_2024-01-01: actions=["Login", "Logout"], summary="活跃交易日..."
# - alice_2024-01-02: actions=["Login"], summary="简短会话..."

# 跨时间的语义搜索
results = memory.search("Alice 什么时候感到沮丧？", top_k=1)
```

完整的工作示例，见 [examples/06_temporal_memory_consolidation.py](examples/06_temporal_memory_consolidation.py)

</details>


## 🔍 语义搜索

构建索引并通过自然语言搜索：

```python
# 构建向量索引
experience_memory.build_index()

# 语义搜索
results = experience_memory.search("调试 Python 异常堆栈溢出", top_k=5)

for experience in results:
    print(f"- {experience.error_signature}")
    print(f"  解决方案: {experience.solutions}")
```


## 🛠️ 合并策略

选择如何处理冲突：

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| `MERGE_FIELD` | 非空覆盖、列表追加 | 简单属性收集 |
| `KEEP_INCOMING` | 最新数据优先 | 状态更新（当前角色、最后在线时间） |
| `KEEP_EXISTING` | 首个观察保留 | 历史记录（首次发布年份） |
| `LLM.BALANCED` | **LLM 驱动的语义合并** | 复杂综合、矛盾解决 |
| `LLM.PREFER_INCOMING` | **LLM 语义合并，语义冲突优先新数据** | 新信息应在出现矛盾时优先考虑 |
| `LLM.PREFER_EXISTING` | **LLM 语义合并，语义冲突优先旧数据** | 现有数据应在出现矛盾时优先考虑 |
| `LLM.CUSTOM_RULE` | **用户自定义的合并逻辑，带有动态上下文** | 特定领域的规则、上下文感知的合并 |

```python
# 示例：LLM 智能合并冲突的信息
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.LLM.BALANCED  # 或 LLM.PREFER_INCOMING、LLM.PREFER_EXISTING、LLM.CUSTOM_RULE
)
```

<details>
<summary><b>🔧 自定义合并规则（高级）</b></summary>

**注入你自己的合并逻辑**，支持静态规则和动态上下文：

```python
from datetime import datetime

# 定义一个动态规则函数（在合并时动态计算）
def get_time_context():
    hour = datetime.now().hour
    if hour >= 9 and hour <= 17:
        return "工作时间：优先使用稳定、经过验证的数据"
    else:
        return "非工作时间：优先使用最新更新"

# 使用 CUSTOM_RULE，结合静态规则 + 动态上下文
memory = OMem(
    memory_schema=BugFixExperience,
    key_extractor=lambda x: x.error_signature,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.CUSTOM_RULE,
    rule="""
    智能合并调试经验：
    - 将所有独特的解决方案合并为列表
    - 综合预防提示，融入领域上下文
    - 保留最近的解决方案作为主要建议
    """,
    dynamic_rule=get_time_context  # 在合并时动态计算！
)

# 使用示例：错误随时间演变
memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: pandas",
    solutions=["pip install pandas"],
    prevention_tips="先检查 requirements.txt"
))

memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: pandas",
    solutions=["使用 conda-forge 镜像"],
    prevention_tips="在限制网络中，尝试 conda"
))

# 结果：LLM 在考虑 dynamic_rule 的时间上下文后合并两者
result = memory.get("ModuleNotFoundError: pandas")
print(result.prevention_tips)
# >>> "先检查 requirements.txt。在限制网络中，使用 conda-forge 镜像..."
```

**何时使用 CUSTOM_RULE**：
- 复杂的特定领域合并逻辑
- 时间/上下文感知的决策（如"凌晨 2 点优先旧数据，白天优先新数据"）
- 环保境特定规则（如"生产环保：保守策略，测试环保：激进策略"）
- LLM 策略无法覆盖的多因素决策

</details>


<details>
<summary><b>⚡ 控制 LLM 并发（v0.1.5+）</b></summary>

在使用 **LLM 驱动的合并策略**（`LLM.BALANCED`、`LLM.PREFER_INCOMING`、`LLM.PREFER_EXISTING`、`LLM.CUSTOM_RULE`）时，OntoMem 会向你的 LLM 提供商发起批量 API 调用。默认情况下，这些请求可能并发进行，这会导致触发速率限制或 API 限流。

### 使用 `max_workers` 参数

使用 `max_workers` 参数控制并发 LLM 请求的最大数量：

```python
memory = OMem(
    memory_schema=UserProfile,
    key_extractor=lambda x: x.uid,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.BALANCED,
    max_workers=3  # 限制最多 3 个并发请求
)
```

### 配置指南

| 场景 | 推荐 `max_workers` | 说明 |
|------|------------------|------|
| **开发/测试** | `2-3` | 保守配置，防止 API 错误 |
| **生产（小规模）** | `3-5` | 默认值：5。速度与安全的平衡 |
| **生产（大规模）** | `5-10+` | 取决于你的 LLM 提供商账户级别 |
| **API 被限流** | `1-2` | 最安全：串行或半并行处理 |

### 调优技巧

1. **保守开始**：从 `max_workers=2` 开始确保稳定性
2. **监测性能**：检查合并时间和错误率
3. **逐步增加**：如果稳定，尝试 `max_workers=5`，然后更高
4. **检查限制**：验证你的 OpenAI 账户等级的速率限制（每分钟请求数）
5. **观察错误**：如果看到 `RateLimitError`，降低 `max_workers`

**示例：生产环保设置**
```python
import os

# 从环境变量读取
max_workers = int(os.getenv("ONTOMEM_MAX_WORKERS", 3))

memory = OMem(
    memory_schema=UserProfile,
    key_extractor=lambda x: x.uid,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.BALANCED,
    max_workers=max_workers  # 不修改代码即可调整
)
```

> **注意**：`max_workers` 参数仅影响 LLM 驱动的合并策略。经典策略（`MERGE_FIELD`、`KEEP_INCOMING`、`KEEP_EXISTING`）不使用 LLM，不受影响。

</details>


## 💾 保存与加载

快照你的完整记忆状态：

```python
# 保存（结构化数据 → memory.json，向量 → FAISS 索引）
experience_memory.dump("./debug_knowledge")

# 稍后快速恢复
new_memory = OMem(...)
new_memory.load("./debug_knowledge")
```


## 🔧 安装与设置

### 基础安装

```bash
pip install ontomem
```

或使用 `uv`：
```bash
uv add ontomem
```

<details>
<summary><b>📦 为开发者</b></summary>

要设置包含所有测试和文档工具的开发环境：

```bash
uv sync --group dev
```

**核心需求：**
- Python 3.11+
- LangChain（用于 LLM 集成）
- Pydantic（用于模式定义）
- FAISS（用于向量搜索）

</details>


## 👨‍💻 作者

**Yifan Feng** - [evanfeng97@gmail.com](mailto:evanfeng97@gmail.com)


## 🤝 贡献

我们在构建下一代 AI 记忆标准。欢迎 PR 和 Issue！


## 📝 许可证

根据 Apache License, Version 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

您可以在 Apache License 2.0 的条款下自由使用、修改和分发此软件。


**由相信“记忆不只是搜索”的 AI 开发者用 ❤️ 构建。**
