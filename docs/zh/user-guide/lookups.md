# Lookups：快速查询的二级索引

## 概览

**Lookups** 功能为 OMem 提供了基于哈希的二级索引，实现通过自定义键进行 **O(1) 快速查询**，无需向量嵌入的开销。

与向量索引（FAISS）执行语义相似度搜索不同，Lookups 对指定字段进行精确匹配，补充了你的语义记忆系统。

## 核心特性

✨ **多维索引**：为不同的字段创建无限多个查找表（名字、地点、时间等）  
✨ **自动维护**：当项目合并或删除时，索引自动更新  
✨ **内存高效**：仅存储引用（主键），不复制数据  
✨ **数据一致**：无过期数据——查找表始终反映内存的当前状态  

## 快速开始

### 1. 创建查找表

```python
from ontomem import OMem, MergeStrategy
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

memory = OMem(
    memory_schema=Event,
    key_extractor=lambda x: x.id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.MERGE_FIELD
)

# 为不同维度创建索引
memory.create_lookup("by_name", lambda x: x.char_name)
memory.create_lookup("by_location", lambda x: x.location)
```

### 2. 添加数据

```python
events = [
    Event(id="evt_001", char_name="小红", location="厨房", ...),
    Event(id="evt_002", char_name="小明", location="厨房", ...),
    Event(id="evt_003", char_name="小红", location="客厅", ...),
]
memory.add(events)
```

### 3. 通过 Lookups 查询

```python
# O(1) 快速按名字查询
xiaohong_events = memory.get_by_lookup("by_name", "小红")
# 返回: [evt_001, evt_003]

# O(1) 快速按位置查询
kitchen_events = memory.get_by_lookup("by_location", "厨房")
# 返回: [evt_001, evt_002]

# 结合向量搜索
memory.build_index()
semantic_results = memory.search("早上的活动", top_k=5)
```

## API 参考

### `create_lookup(name: str, key_extractor: Callable[[T], Any]) -> None`

创建一个新的二级查找表。

**参数：**
- `name`: 这个查找表的唯一标识符（例如 "by_name"、"by_location"）
- `key_extractor`: 从实体中提取查找键的函数

**异常：**
- `ValueError`: 如果已存在同名的查找表

**示例：**
```python
memory.create_lookup("by_date", lambda x: x.timestamp[:10])  # YYYY-MM-DD
```

### `get_by_lookup(lookup_name: str, lookup_key: Any) -> List[T]`

检索匹配查找键的项。

**参数：**
- `lookup_name`: 要查询的查找表名称
- `lookup_key`: 要匹配的值

**返回：**
- 匹配该键的实体列表。如果查找表或键不存在，返回空列表。

**示例：**
```python
results = memory.get_by_lookup("by_date", "2024-01-15")
```

### `drop_lookup(name: str) -> bool`

删除一个查找表。

**参数：**
- `name`: 要删除的查找表名称

**返回：**
- 删除成功返回 `True`，查找表不存在返回 `False`

**示例：**
```python
memory.drop_lookup("by_location")
```

### `list_lookups() -> List[str]`

列出所有已注册的查找表名称。

**返回：**
- 当前活跃的查找表名称列表

**示例：**
```python
print(memory.list_lookups())  # ['by_name', 'by_location', 'by_date']
```

## 合并时的数据一致性

Lookups 的关键特性是**在项目合并时自动保持一致性**。

### 场景

1. 你有 `evt_001` 在 "厨房"
2. 查找表状态：`"厨房" → {evt_001}`
3. 添加 `evt_001` 且 location="客厅"（同 ID，不同位置）
4. 自动触发合并（采用较新的值）

### 结果

- 旧的查找表条目 `"厨房" → evt_001` 被**删除**
- 新的查找表条目 `"客厅" → evt_001` 被**添加**
- 没有过期数据！

### 实现原理

OMem 使用**快照策略**：

```python
# 合并前：保存旧状态
old_item = storage[pk]

# 执行合并
merged_item = merger.merge([old_item, new_item])
storage[pk] = merged_item

# 更新所有查找表
# - 使用旧项状态从查找表中删除
# - 使用合并后的项状态添加到查找表
```

## 使用场景

### 1. 具有多维的时间序列数据

```python
class GameEvent(BaseModel):
    id: str          # 主键
    char_name: str   # 谁
    location: str    # 哪里
    timestamp: str   # 什么时候
    action: str      # 做了什么

memory.create_lookup("by_character", lambda x: x.char_name)
memory.create_lookup("by_location", lambda x: x.location)
memory.create_lookup("by_hour", lambda x: x.timestamp.split(':')[0])

# 查找涉及某个角色的所有事件
character_history = memory.get_by_lookup("by_character", "小红")

# 查找某个地点发生的所有事件
location_events = memory.get_by_lookup("by_location", "厨房")

# 查找早上时间段的所有事件
morning_events = memory.get_by_lookup("by_hour", "08")
```

### 2. 用户档案管理

```python
class UserProfile(BaseModel):
    user_id: str
    email: str
    company: str
    department: str
    skills: list[str]

memory.create_lookup("by_email", lambda x: x.email)
memory.create_lookup("by_company", lambda x: x.company)
memory.create_lookup("by_department", lambda x: f"{x.company}:{x.department}")

# 快速查找
user = memory.get_by_lookup("by_email", "alice@example.com")[0]
company_users = memory.get_by_lookup("by_company", "TechCorp")
dept_users = memory.get_by_lookup("by_department", "TechCorp:Engineering")
```

### 3. 分层数据

```python
# 复合键用于分层查询
memory.create_lookup(
    "by_location_hour",
    lambda x: f"{x.location}:{x.timestamp.split(':')[0]}"
)

# 查询：厨房在 08:00 的事件
results = memory.get_by_lookup("by_location_hour", "厨房:08")
```

## 性能特征

| 操作 | 复杂度 | 备注 |
|------|-------|------|
| 创建查找表 | O(n) | 一次性成本（n = 现有项数） |
| 查询 | **O(1)** | 哈希查找 |
| 检索匹配项 | O(m) | m = 匹配项数 |
| 添加项 | O(l) | l = 查找表数量 |
| 删除项 | O(l) | 在所有查找表上清理 |
| 合并项 | O(l) | 每个查找表上删除旧 + 添加新 |

### 内存开销

Lookups 仅存储引用（主键），最小化内存：

```
场景：1,000,000 个项目，10 个查找表，每个查找表 100 个唯一值
内存：~4-10 MB（0.001-0.01% 的存储）
```

相比之下，向量索引通常消耗 10-50% 的存储空间。

## 最佳实践

### ✅ 应该做

- **在添加大量数据之前**创建查找表
- 为**精确匹配**特定字段使用查找表
- 将查找表与向量搜索结合进行强大的查询
- 删除未使用的查找表以节省内存
- 对查找键使用可哈希的类型（str, int, tuple）

### ❌ 不应该做

- 使用查找表进行模糊/部分匹配（使用向量搜索代替）
- 为每个可能的字段创建查找表（要有选择性）
- 在查找表中存储 `None` 值（会跳过并显示警告）
- 依赖查找表进行子字符串匹配（不支持）

## 将 Lookups 与向量搜索结合

同时获得两者的优势：

```python
# 步骤 1：使用 Lookups 进行精确过滤
kitchen_events = memory.get_by_lookup("by_location", "厨房")

# 步骤 2：对过滤结果进行语义搜索
relevant_kitchen_events = [
    e for e in kitchen_events 
    if e in memory.search("烹饪活动", top_k=100)
]

# 或反过来
relevant_in_memory = memory.search("烹饪", top_k=50)
kitchen_relevant = [
    e for e in relevant_in_memory
    if e in memory.get_by_lookup("by_location", "厨房")
]
```

## 常见问题

### Q: "Lookup 'by_name' already exists"（查找表已存在）

A: 你尝试创建一个已存在的同名查找表。先使用 `drop_lookup()` 或使用不同的名称。

```python
memory.drop_lookup("by_name")
memory.create_lookup("by_name", new_extractor)
```

### Q: 我的查找表返回空结果

A: 常见原因：
1. **键值拼写错误**：检查你使用的确切值
2. **提取器不匹配**：验证提取器返回你查询的值
3. **None 值**：某些项的提取器可能返回 `None`

### Q: 合并后查找表不一致

这不应该发生。如果发生了，请提交 issue。查找表在每次合并时自动更新。

## 迁移指南

如果你之前进行手动索引：

**之前：**
```python
# 手动索引维护
name_index = {}
for item in memory.items:
    if item.name not in name_index:
        name_index[item.name] = []
    name_index[item.name].append(item)

# 手动查询
xiaohong = name_index.get("小红", [])
```

**之后：**
```python
# 自动使用 Lookups
memory.create_lookup("by_name", lambda x: x.name)
xiaohong = memory.get_by_lookup("by_name", "小红")
```

Lookups 功能自动处理所有维护工作，包括在合并和删除期间的更新。

## 参考资源

- [向量搜索指南](../basic-concepts.md) - 了解使用向量索引的语义搜索
- [合并策略指南](../user-guide/merge-strategies.md) - 理解重复检测和合并的工作原理
- [API 参考](../api/core/overview.md) - 完整的 OMem API 文档
