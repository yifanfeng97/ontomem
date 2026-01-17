# Merger Module

API reference for merge strategy implementations.

## Merger Strategies

Each merge strategy class inherits from either `BaseMerger` or `BaseLLMMerger`.

### Classic Mergers

#### KeepIncomingMerger
Always use the incoming (latest) data.

```python
from ontomem.merger import KeepIncomingMerger

merger = KeepIncomingMerger()
result = merger.merge(existing, incoming)  # Returns incoming
```

#### KeepExistingMerger
Always preserve the first (existing) data.

```python
from ontomem.merger import KeepExistingMerger

merger = KeepExistingMerger()
result = merger.merge(existing, incoming)  # Returns existing
```

#### FieldMerger
Non-null overwrites, lists append (default).

```python
from ontomem.merger import FieldMerger

merger = FieldMerger()
result = merger.merge(existing, incoming)  # Smart merge
```

### LLM-Powered Mergers

Require `llm_client` for intelligent synthesis.

#### PreferIncomingMerger
LLM synthesis preferring new data on conflicts.

#### PreferExistingMerger
LLM synthesis preferring existing data on conflicts.

#### BalancedMerger
LLM synthesis balancing both perspectives.

---

See [Merge Strategies Guide](../../user-guide/merge-strategies.md) for usage examples.
