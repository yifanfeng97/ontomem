# Merger 模块

合并策略实现的 API 参考。

## 合并策略

每个合并策略类继承自 `BaseMerger` 或 `BaseLLMMerger`。

### 经典 Mergers

#### KeepIncomingMerger
始终使用传入（最新）数据。

```python
from ontomem.merger import KeepIncomingMerger

merger = KeepIncomingMerger()
result = merger.merge(existing, incoming)  # 返回 incoming
```

#### KeepExistingMerger
始终保留首次（现有）数据。

```python
from ontomem.merger import KeepExistingMerger

merger = KeepExistingMerger()
result = merger.merge(existing, incoming)  # 返回 existing
```

#### FieldMerger
非空覆盖、列表追加（默认）。

```python
from ontomem.merger import FieldMerger

merger = FieldMerger()
result = merger.merge(existing, incoming)  # 智能合并
```

### LLM 驱动的 Mergers

需要 `llm_client` 进行智能综合。

#### PreferIncomingMerger
LLM 综合，在冲突时优先新数据。

#### PreferExistingMerger
LLM 综合，在冲突时优先现有数据。

#### BalancedMerger
LLM 综合，平衡两种观点。

---

查看[合并策略指南](../../user-guide/merge-strategies.md)了解使用示例。
