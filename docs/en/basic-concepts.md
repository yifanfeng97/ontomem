# Basic Concepts

Understand the core concepts that make OntoMem work.

## Schema-First Design

OntoMem uses **Pydantic** models to define the structure of your memories. This ensures type safety and IDE support.

```python
from pydantic import BaseModel
from typing import List, Optional

class ResearcherProfile(BaseModel):
    """Type-safe researcher profile."""
    name: str  # Required field
    affiliation: str
    research_interests: List[str]
    h_index: Optional[int] = None  # Optional field with default
```

Benefits:
- ✅ IDE autocomplete and type hints
- ✅ Automatic validation
- ✅ Easy serialization (JSON/dict)
- ✅ Clear data contracts

## Unique Keys & Deduplication

Every entity needs a **unique key** to prevent duplicates:

```python
memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,  # Extract the unique key
)
```

When you add an entity with an existing key, OntoMem **merges** it instead of creating a duplicate.

## Merge Strategies

Different scenarios require different merging approaches:

### FIELD_MERGE (Default)
- Non-null fields overwrite
- Lists are appended
- Simple and predictable

```python
memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,
    merge_strategy=MergeStrategy.FIELD_MERGE
)
```

### KEEP_INCOMING
- Always use the latest (incoming) data
- Useful for status updates

### KEEP_EXISTING
- Always preserve the first observation
- Useful for historical records

### LLM.BALANCED (LLM-Powered)
- Intelligently synthesize conflicting information
- Requires LLM client
- Best for complex, multi-faceted data

## Hybrid Search

OntoMem offers two ways to find memories:

### 1. Key-Based Lookup (O(1))

```python
researcher = memory.get("Yann LeCun")
```

Fast, exact match. Use when you know the unique key.

### 2. Semantic Search (Vector-Based)

```python
memory.build_index()
results = memory.search("deep learning neural networks", k=5)
```

Uses embeddings to find semantically similar entities. Great for discovery.

## State Management

### In-Memory Operations

```python
# Add items
memory.add(researcher_profile)

# Query
profile = memory.get("Yann LeCun")

# Update (add duplicate key triggers merge)
memory.add(updated_profile)

# Remove
memory.remove("Yann LeCun")

# Clear all
memory.clear()
```

### Persistence

```python
# Save state to disk
memory.dump("./my_memory")

# Load state in new session
new_memory = OMem(...)
new_memory.load("./my_memory")
```

## Batch Operations

```python
# Add multiple items at once
researchers = [prof1, prof2, prof3]
memory.add(researchers)

# Iterate over all
for researcher in memory.items:
    print(researcher.name)

# Get all keys
keys = memory.keys  # List[Any]

# Get count
size = memory.size  # int
```

## Next Steps

- Learn about [Merge Strategies](../user-guide/merge-strategies.md) in detail
- Explore [Advanced Usage](../user-guide/advanced-usage.md)
- Check out [Examples](../examples/examples-overview.md)

---

**Ready to build?** Start with the [Quick Start](quick-start.md) guide.
