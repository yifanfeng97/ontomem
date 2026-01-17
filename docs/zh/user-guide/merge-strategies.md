# 合并策略指南

学习如何为你的用例选择和实施正确的合并策略。

## 概述

Ontomem 支持 6 种合并策略来处理更新实体时的冲突：

| 策略 | 类别 | 行为 | 适用场景 |
|------|------|------|---------|
| `FIELD_MERGE` | 经典 | 非空覆盖、列表追加 | 默认选择、简单场景 |
| `KEEP_INCOMING` | 经典 | 始终使用最新数据 | 状态更新、当前状态 |
| `KEEP_EXISTING` | 经典 | 始终保留首次观察 | 历史记录、时间戳 |
| `LLM.BALANCED` | LLM | 智能综合两者 | 复杂矛盾 |
| `LLM.PREFER_INCOMING` | LLM | 冲突时优先新数据 | 新信息应优先 |
| `LLM.PREFER_EXISTING` | LLM | 冲突时优先旧数据 | 旧信息应优先 |

## 经典策略

### FIELD_MERGE（默认）

**行为**：非空字段覆盖，列表被追加。

```python
from ontomem import OMem, MergeStrategy

memory = OMem(
    memory_schema=Profile,
    key_extractor=lambda x: x.id,
    merge_strategy=MergeStrategy.FIELD_MERGE
)

# 第 1 天
memory.add(Profile(
    id="user1",
    name="Alice",
    interests=["AI", "ML"]
))

# 第 2 天：合并操作
memory.add(Profile(
    id="user1",
    name="Alice Johnson",  # 非空：覆盖 "Alice"
    interests=["NLP"]       # 列表：追加到 ["AI", "ML"]
))

result = memory.get("user1")
# 结果：name="Alice Johnson", interests=["AI", "ML", "NLP"]
```

**何时使用**：大多数场景的默认选择。

---

### KEEP_INCOMING

**行为**：始终使用传入（最新）数据。

```python
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.KEEP_INCOMING
)

# 第 1 天：初始状态
memory.add(Profile(
    user_id="user1",
    status="offline",
    last_seen="2024-01-01"
))

# 第 2 天：用户现在在线
memory.add(Profile(
    user_id="user1",
    status="online",  # 将被覆盖
    last_seen="2024-01-15"  # 将被覆盖
))

result = memory.get("user1")
# 结果：status="online", last_seen="2024-01-15"
```

**何时使用**：
- 用户在线状态追踪
- 实时状态更新
- 当前位置/角色
- 最新传感器读数

---

### KEEP_EXISTING

**行为**：始终保留首次观察。

```python
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.KEEP_EXISTING
)

# 第 1 天：首次发表
memory.add(Paper(
    doi="10.1234/example",
    title="Original Title",
    year=2020
))

# 第 5 天：尝试更新（将被忽略）
memory.add(Paper(
    doi="10.1234/example",
    title="Updated Title",
    year=2024
))

result = memory.get("10.1234/example")
# 结果：title="Original Title", year=2020（未改变）
```

**何时使用**：
- 首次发表日期（永不改变）
- 首次观察时间戳
- 原始名称/标识符
- 历史记录

---

## LLM 驱动的策略

LLM 策略使用 LLM 客户端**智能综合**冲突信息。

### 设置

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

memory = OMem(
    memory_schema=Profile,
    key_extractor=lambda x: x.id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)
```

### LLM.BALANCED

**行为**：LLM 将两个观察综合为连贯、统一的记录。

```python
# 关于研究人员的冲突信息
memory.add(ResearcherProfile(
    name="John Smith",
    affiliation="University A",
    research_focus="Computer Vision"
))

# 稍后带有不同信息的更新
memory.add(ResearcherProfile(
    name="John Smith",
    affiliation="University B",  # 冲突！
    research_focus="Machine Learning"  # 冲突！
))

# LLM 综合：
result = memory.get("John Smith")
# 结果可能是：
# {
#   "affiliation": "University A（2023 年移至 University B）",
#   "research_focus": "计算机视觉和机器学习",
#   "note": "研究人员将焦点从 CV 转向更广泛的 ML"
# }
```

**何时使用**：需要细致合并的复杂、多面数据。

---

### LLM.PREFER_INCOMING

**行为**：LLM 语义合并，但冲突时**优先新数据**。

```python
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.LLM.PREFER_INCOMING
)

# 原始观察
memory.add(Company(
    name="TechCorp",
    description="一个软件公司",
    ceo="John Doe"
))

# 更新信息
memory.add(Company(
    name="TechCorp",
    description="领先的 AI/ML 解决方案提供商",  # 新信息
    ceo="Jane Smith"  # 新 CEO
))

# LLM 综合但优先传入数据：
result = memory.get("TechCorp")
# 结果优先选择："Jane Smith" 作为 CEO，更新的描述
```

**何时使用**：
- 随时间演变的实体
- 新信息通常应该覆盖的情况
- 角色变更、技术转向
- 当前 vs 历史背景

---

### LLM.PREFER_EXISTING

**行为**：LLM 语义合并，但冲突时**优先旧数据**。

```python
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.LLM.PREFER_EXISTING
)

# 首次观察（权威性）
memory.add(Person(
    name="Albert Einstein",
    birth_year=1879,
    field="Physics"
))

# 稍后冲突更新
memory.add(Person(
    name="Albert Einstein",
    birth_year=1880,  # 错误！
    field="Physics and Philosophy"
))

# LLM 综合但优先现有数据：
result = memory.get("Albert Einstein")
# 结果保留：birth_year=1879，使用权威首条记录
```

**何时使用**：
- 传记数据（出生年份、原始名称）
- 首次记录观察最可靠
- 科学事实
- 不可变历史记录

---

## 策略比较

```python
# 同一场景使用不同策略：

profile_v1 = Profile(
    id="alice",
    experience_years=5,
    skills=["Python", "ML"]
)

profile_v2 = Profile(
    id="alice",
    experience_years=7,  # 冲突
    skills=["Python", "ML", "DevOps"]
)

# FIELD_MERGE
# 结果：experience_years=7, skills=["Python", "ML", "DevOps"]

# KEEP_INCOMING
# 结果：experience_years=7, skills=["Python", "ML", "DevOps"]

# KEEP_EXISTING
# 结果：experience_years=5, skills=["Python", "ML"]

# LLM.BALANCED
# 结果："7 年（从 5 年进展）"，包括所有技能和上下文

# LLM.PREFER_INCOMING
# 结果：优先 7 年和新技能，可能注明进展

# LLM.PREFER_EXISTING
# 结果：保留 5 年，但包括新 DevOps 技能上下文
```

## 选择策略

### 决策树

```
你的数据是否随时间改变？
├─ 是，新数据更准确 → KEEP_INCOMING 或 LLM.PREFER_INCOMING
├─ 是，但旧数据更准确 → KEEP_EXISTING 或 LLM.PREFER_EXISTING
├─ 是，两者同等重要 → LLM.BALANCED
└─ 否，永不改变 → KEEP_EXISTING

你的数据是否复杂/多面？
├─ 简单字段 → FIELD_MERGE
└─ 复杂关系/矛盾 → LLM.* 策略
```

### 快速参考

- 🎯 **默认**：`FIELD_MERGE` - 适用于大多数情况
- ⚡ **状态更新**：`KEEP_INCOMING` - 最新优先
- 📚 **历史**：`KEEP_EXISTING` - 首先优先
- 🧠 **复杂逻辑**：`LLM.BALANCED` - 智能综合
- 🔄 **演变数据**：`LLM.PREFER_INCOMING` - 新数据优先
- 🏛️ **权威**：`LLM.PREFER_EXISTING` - 原始为真

---

## 性能考虑

| 策略 | 速度 | 成本 | 备注 |
|------|------|------|------|
| FIELD_MERGE | ⚡⚡⚡ | 免费 | 无 API 调用 |
| KEEP_INCOMING | ⚡⚡⚡ | 免费 | 无 API 调用 |
| KEEP_EXISTING | ⚡⚡⚡ | 免费 | 无 API 调用 |
| LLM.BALANCED | ⚡ | LLM tokens | 每次合并约 500-1000 tokens |
| LLM.PREFER_INCOMING | ⚡ | LLM tokens | 每次合并约 500-1000 tokens |
| LLM.PREFER_EXISTING | ⚡ | LLM tokens | 每次合并约 500-1000 tokens |

**提示**：对于高频更新使用经典策略，LLM 策略谨慎用于重要整合。

---

## 下一步

- 查看[示例](../examples/examples-overview.md)获取真实用法
- 探索[高级用法](advanced-usage.md)
- 检查 [API 参考](../api/overview.md)获取详情

---

**有问题？** 查看我们的 [FAQ](../faq.md)。
