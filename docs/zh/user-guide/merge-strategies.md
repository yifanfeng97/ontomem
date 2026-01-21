# 合并策略指南

学习如何为你的用例选择和实施正确的合并策略。

## 概述

OntoMem 支持 7 种合并策略来处理更新实体时的冲突：

| 策略 | 类别 | 行为 | 适用场景 |
|------|------|------|---------|
| `MERGE_FIELD` | 经典 | 非空覆盖、列表追加 | 默认选择、简单场景 |
| `KEEP_INCOMING` | 经典 | 始终使用最新数据 | 状态更新、当前状态 |
| `KEEP_EXISTING` | 经典 | 始终保留首次观察 | 历史记录、时间戳 |
| `LLM.BALANCED` | LLM | 智能综合两者 | 复杂矛盾 |
| `LLM.PREFER_INCOMING` | LLM | 冲突时优先新数据 | 新信息应优先 |
| `LLM.PREFER_EXISTING` | LLM | 冲突时优先旧数据 | 旧信息应优先 |
| `LLM.CUSTOM_RULE` | LLM | 用户定义的逻辑和动态上下文 | 高级、特定领域的规则 |

## 经典策略

### MERGE_FIELD（默认）

**行为**：非空字段覆盖，列表被追加。

```python
from ontomem import OMem, MergeStrategy

memory = OMem(
    memory_schema=Profile,
    key_extractor=lambda x: x.id,
    strategy_or_merger=MergeStrategy.MERGE_FIELD
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
    strategy_or_merger=MergeStrategy.KEEP_INCOMING
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
    strategy_or_merger=MergeStrategy.KEEP_EXISTING
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
    strategy_or_merger=MergeStrategy.LLM.BALANCED
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
    strategy_or_merger=MergeStrategy.LLM.PREFER_INCOMING
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
    strategy_or_merger=MergeStrategy.LLM.PREFER_EXISTING
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

## 自定义合并规则（Custom Rules）

对于内置策略无法满足的高级场景，你可以使用 `MergeStrategy.LLM.CUSTOM_RULE` 定义自己的合并逻辑。这允许你提供自然语言指令，并在运行时注入动态上下文。

### 参数

- **`rule`** (str): 静态指令字符串，用自然语言描述如何处理冲突，引导 LLM 按照你的具体合并逻辑进行操作。
- **`dynamic_rule`** (Callable[[], str], 可选): 在运行时返回字符串的函数。用于注入基于时间的逻辑、环境变量或智能体状态。

### 基础示例

```python
from ontomem.merger import create_merger, MergeStrategy

merger = create_merger(
    strategy=MergeStrategy.LLM.CUSTOM_RULE,
    key_extractor=lambda x: x.id,
    llm_client=llm,
    item_schema=UserProfile,
    rule="智能合并用户档案。如果现有数据和传入数据之间出现冲突，优先使用 GitHub 来源的数据。始终保留最完整的生物描述。"
)

# 在记忆中使用
memory = OMem(
    memory_schema=UserProfile,
    key_extractor=lambda x: x.id,
    strategy_or_merger=merger,
    llm_client=llm,
    embedder=embedder
)
```

### 动态规则

动态规则在运行时评估，允许你的合并策略根据上下文进行自适应。

```python
from datetime import datetime

def get_time_aware_context():
    """将基于时间的逻辑注入合并规则。"""
    hour = datetime.now().hour
    if hour > 18:
        return "当前时间：晚上。优先接受最近的更新，因为它们更新鲜。"
    else:
        return "当前时间：工作时间。优先使用已验证的、稳定的数据。"

merger = create_merger(
    strategy=MergeStrategy.LLM.CUSTOM_RULE,
    key_extractor=lambda x: x.id,
    llm_client=llm,
    item_schema=UserProfile,
    rule="智能合并用户档案。优先使用最新的电子邮件地址，保留所有唯一的技能。",
    dynamic_rule=get_time_aware_context
)
```

### 真实示例：环境感知的合并

```python
import os

def get_environment_rules():
    """根据部署环境调整合并规则。"""
    env = os.getenv("ENVIRONMENT", "dev")
    if env == "production":
        return "生产环境模式：使用保守合并策略。仅接受来自已验证来源的更新。如有疑问，保留现有数据。"
    else:
        return "开发环境模式：接受所有传入更新，以加快迭代和测试。"

merger = create_merger(
    strategy=MergeStrategy.LLM.CUSTOM_RULE,
    key_extractor=lambda x: x.id,
    llm_client=llm,
    item_schema=Company,
    rule="通过整合所有唯一信息来合并公司记录。",
    dynamic_rule=get_environment_rules
)
```

### 时间序列整合示例

```python
from datetime import datetime

class DailyReport(BaseModel):
    employee_id: str
    date: str
    tasks_completed: int
    mood: str

def get_consolidation_context():
    """根据报告时间调整整合逻辑。"""
    now = datetime.now()
    day_name = now.strftime("%A")
    return f"今天是{day_name}。周中的报告应平衡所有任务。周末的报告应总结整周。"

# 复合键：employee_id + date 用于日级整合
memory = OMem(
    memory_schema=DailyReport,
    key_extractor=lambda x: f"{x.employee_id}_{x.date}",
    strategy_or_merger=create_merger(
        strategy=MergeStrategy.LLM.CUSTOM_RULE,
        rule="将多个每日更新整合成一个连贯的日报。对任务数求和，合成情绪描述。",
        dynamic_rule=get_consolidation_context
    ),
    llm_client=llm
)
```

**何时使用**：
- 复杂的、特定领域的合并逻辑
- 依赖于上下文的合并（时间、环境、状态）
- 高级数据质量规则
- 具有特定优先级的多源协调

---

## 控制 LLM 并发

使用 LLM 驱动的合并策略时，OntoMem 会向你的 LLM 提供商发起批量 API 调用。默认情况下，这些请求可能并发进行，可能会触发速率限制或 API 限流。`max_workers` 参数允许你控制最大并发 LLM 请求数。

### `max_workers` 参数

使用 `max_workers` 限制并发 API 调用：

```python
from ontomem import OMem, MergeStrategy

memory = OMem(
    memory_schema=Profile,
    key_extractor=lambda x: x.id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.BALANCED,
    max_workers=3  # 限制最多 3 个并发请求
)
```

或使用 `create_merger`：

```python
from ontomem.merger import create_merger, MergeStrategy

merger = create_merger(
    strategy=MergeStrategy.LLM.BALANCED,
    key_extractor=lambda x: x.id,
    llm_client=llm,
    item_schema=Profile,
    max_workers=2  # 对被限流的账户采用更保守的配置
)
```

### 配置建议

| 场景 | 推荐值 | 说明 |
|------|--------|------|
| 开发/测试 | `2-3` | 保守配置，防止 API 错误 |
| 生产（小规模） | `3-5` | 默认值：5。速度与安全的平衡 |
| 生产（大规模） | `5-10+` | 取决于你的 LLM 提供商账户级别 |
| API 被限流 | `1-2` | 最安全：串行或半并行处理 |

### 调优指南

1. **保守开始**：从 `max_workers=2` 开始确保稳定性
2. **监测性能**：检查合并时间和错误率
3. **逐步增加**：如果稳定，尝试更高的值
4. **检查限制**：查看你的 OpenAI/提供商账户级别的速率限制（请求/分钟）
5. **处理错误**：如果看到 `RateLimitError`，进一步降低 `max_workers`

### 生产示例

```python
import os
from ontomem import OMem, MergeStrategy

# 从环境变量读取，便于在不修改代码的情况下调整
max_workers = int(os.getenv("ONTOMEM_MAX_WORKERS", "3"))

memory = OMem(
    memory_schema=Profile,
    key_extractor=lambda x: x.id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.BALANCED,
    max_workers=max_workers
)
```


### 重要说明

- **默认值**：`max_workers=5` 为大多数部署提供了良好的平衡
- **经典策略不受影响**：`MERGE_FIELD`、`KEEP_INCOMING`、`KEEP_EXISTING` 不使用 LLM，不受此参数影响
- **LLM 策略**：适用于 `LLM.BALANCED`、`LLM.PREFER_INCOMING`、`LLM.PREFER_EXISTING`、`LLM.CUSTOM_RULE`
- **向后兼容**：所有现有代码继续使用默认值工作

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

# MERGE_FIELD
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

# LLM.CUSTOM_RULE
# 结果："7 年（从 5 年演进而来）"，所有技能应用自定义逻辑
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
├─ 简单字段 → MERGE_FIELD
└─ 复杂关系/矛盾 → LLM.* 策略
```

### 快速参考

- 🎯 **默认**：`MERGE_FIELD` - 适用于大多数情况
- ⚡ **状态更新**：`KEEP_INCOMING` - 最新优先
- 📚 **历史**：`KEEP_EXISTING` - 首先优先
- 🧠 **复杂逻辑**：`LLM.BALANCED` - 智能综合
- 🔄 **演变数据**：`LLM.PREFER_INCOMING` - 新数据优先
- 🏛️ **权威**：`LLM.PREFER_EXISTING` - 原始为真
- ✨ **自定义规则**：`LLM.CUSTOM_RULE` - 用户定义的逻辑，支持运行时上下文

---

## 性能考虑

| 策略 | 速度 | 成本 | 备注 |
|------|------|------|------|
| MERGE_FIELD | ⚡⚡⚡ | 免费 | 无 API 调用 |
| KEEP_INCOMING | ⚡⚡⚡ | 免费 | 无 API 调用 |
| KEEP_EXISTING | ⚡⚡⚡ | 免费 | 无 API 调用 |
| LLM.BALANCED | ⚡ | LLM tokens | 每次合并约 500-1000 tokens |
| LLM.PREFER_INCOMING | ⚡ | LLM tokens | 每次合并约 500-1000 tokens |
| LLM.PREFER_EXISTING | ⚡ | LLM tokens | 每次合并约 500-1000 tokens |
| LLM.CUSTOM_RULE | ⚡ | LLM tokens | 每次合并约 500-1000 tokens + 动态规则评估开销 |

**提示**：对于高频更新使用经典策略，LLM 策略谨慎用于重要整合。

---

## 下一步

- 查看[示例](../examples/examples-overview.md)获取真实用法
- 探索[高级用法](advanced-usage.md)
- 检查 [API 参考](../api/overview.md)获取详情

---

**有问题？** 查看我们的 [FAQ](../faq.md)。
