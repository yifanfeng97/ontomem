# 基本概念

了解 OntoMem 工作的核心概念。

## Schema-First 设计

OntoMem 使用 **Pydantic** 模型来定义你的记忆结构。这确保了类型安全性和 IDE 支持。

```python
from pydantic import BaseModel
from typing import List, Optional

class ResearcherProfile(BaseModel):
    """类型安全的研究人员档案。"""
    name: str  # 必需字段
    affiliation: str
    research_interests: List[str]
    h_index: Optional[int] = None  # 可选字段（带默认值）
```

优势：
- ✅ IDE 自动补全和类型提示
- ✅ 自动验证
- ✅ 轻松序列化（JSON/dict）
- ✅ 清晰的数据契约

## 唯一键 & 去重

每个实体都需要一个**唯一键**来防止重复：

```python
memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,  # 提取唯一键
)
```

当你添加具有现有键的实体时，OntoMem 会**合并**它而不是创建重复。

## 合并策略

不同的场景需要不同的合并方法：

### FIELD_MERGE（默认）
- 非空字段覆盖
- 列表被追加
- 简单可预测

```python
memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,
    merge_strategy=MergeStrategy.FIELD_MERGE
)
```

### KEEP_INCOMING
- 始终使用最新（传入）数据
- 适用于状态更新

### KEEP_EXISTING
- 始终保留首次观察
- 适用于历史记录

### LLM.BALANCED（LLM 驱动）
- 智能综合冲突信息
- 需要 LLM 客户端
- 最适合复杂、多面数据

## 混合搜索

OntoMem 提供两种查找记忆的方式：

### 1. 基于键的查询 (O(1))

```python
researcher = memory.get("Yann LeCun")
```

快速、精确匹配。当你知道唯一键时使用。

### 2. 语义搜索（向量基础）

```python
memory.build_index()
results = memory.search("深度学习神经网络", k=5)
```

使用嵌入来查找语义相似的实体。非常适合发现。

## 状态管理

### 内存中操作

```python
# 添加项目
memory.add(researcher_profile)

# 查询
profile = memory.get("Yann LeCun")

# 更新（添加重复键触发合并）
memory.add(updated_profile)

# 删除
memory.remove("Yann LeCun")

# 清除所有
memory.clear()
```

### 持久化

```python
# 保存状态到磁盘
memory.dump("./my_memory")

# 在新会话中加载状态
new_memory = OMem(...)
new_memory.load("./my_memory")
```

## 批量操作

```python
# 一次添加多个项目
researchers = [prof1, prof2, prof3]
memory.add(researchers)

# 迭代所有项
for researcher in memory.items:
    print(researcher.name)

# 获取所有键
keys = memory.keys  # List[Any]

# 获取计数
size = memory.size  # int
```

## 下一步

- 详细了解[合并策略](../user-guide/merge-strategies.md)
- 探索[高级用法](../user-guide/advanced-usage.md)
- 查看[示例](../examples/examples-overview.md)

---

**准备好开始了吗？** 从[快速开始](quick-start.md)指南开始。
