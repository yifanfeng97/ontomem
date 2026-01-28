# Lookups: Secondary Indices for Fast Retrieval

## Overview

The **Lookups** feature provides hash-based secondary indexing for OMem, enabling **O(1) fast queries** by custom keys without the overhead of vector embeddings.

Unlike the vector index (FAISS) which performs semantic similarity search, Lookups perform exact matching on specified fields, complementing your semantic memory system.

## Key Features

✨ **Multi-dimensional**: Create unlimited lookups for different fields (name, location, time, etc.)  
✨ **Auto-maintained**: Indices automatically update when items are merged or removed  
✨ **Memory efficient**: Stores only references (primary keys), not data copies  
✨ **Consistent**: No stale data - lookups reflect the current state of your memory  

## Quick Start

### 1. Create a Lookup

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

# Create indices for different dimensions
memory.create_lookup("by_name", lambda x: x.char_name)
memory.create_lookup("by_location", lambda x: x.location)
```

### 2. Add Data

```python
events = [
    Event(id="evt_001", char_name="Alice", location="Kitchen", ...),
    Event(id="evt_002", char_name="Bob", location="Kitchen", ...),
    Event(id="evt_003", char_name="Alice", location="LivingRoom", ...),
]
memory.add(events)
```

### 3. Query via Lookups

```python
# Fast O(1) query by name
alice_events = memory.get_by_lookup("by_name", "Alice")
# Returns: [evt_001, evt_003]

# Fast O(1) query by location
kitchen_events = memory.get_by_lookup("by_location", "Kitchen")
# Returns: [evt_001, evt_002]

# Combine with vector search
memory.build_index()
semantic_results = memory.search("morning activities", top_k=5)
```

## API Reference

### `create_lookup(name: str, key_extractor: Callable[[T], Any]) -> None`

Creates a new secondary lookup table.

**Parameters:**
- `name`: Unique identifier for this lookup (e.g., "by_name", "by_location")
- `key_extractor`: Function that extracts the lookup key from an entity

**Raises:**
- `ValueError`: If a lookup with this name already exists

**Example:**
```python
memory.create_lookup("by_date", lambda x: x.timestamp[:10])  # YYYY-MM-DD
```

### `get_by_lookup(lookup_name: str, lookup_key: Any) -> List[T]`

Retrieves items matching a lookup key.

**Parameters:**
- `lookup_name`: Name of the lookup to query
- `lookup_key`: The value to match

**Returns:**
- List of entities matching the key. Returns empty list if lookup or key not found.

**Example:**
```python
results = memory.get_by_lookup("by_date", "2024-01-15")
```

### `drop_lookup(name: str) -> bool`

Removes a lookup table.

**Parameters:**
- `name`: Name of the lookup to remove

**Returns:**
- `True` if removed successfully, `False` if lookup not found

**Example:**
```python
memory.drop_lookup("by_location")
```

### `list_lookups() -> List[str]`

Lists all registered lookup names.

**Returns:**
- List of lookup names currently active

**Example:**
```python
print(memory.list_lookups())  # ['by_name', 'by_location', 'by_date']
```

## Data Consistency During Merge

A key feature of Lookups is **automatic consistency maintenance** when items are merged.

### Scenario

1. You have `evt_001` at "Kitchen"
2. Lookup state: `"Kitchen" → {evt_001}`
3. Add `evt_001` with location="LivingRoom" (same ID, different location)
4. Merge happens automatically (takes newer value)

### Result

- Old lookup entry `"Kitchen" → evt_001` is **removed**
- New lookup entry `"LivingRoom" → evt_001` is **added**
- No stale data!

### Implementation

OMem uses a **Snapshot strategy**:

```python
# Before merge: save old state
old_item = storage[pk]

# Perform merge
merged_item = merger.merge([old_item, new_item])
storage[pk] = merged_item

# Update all lookups
# - Remove old_item from lookups using its state
# - Add merged_item to lookups using its state
```

## Use Cases

### 1. Time-Series Data with Multiple Dimensions

```python
class GameEvent(BaseModel):
    id: str          # Primary key
    char_name: str   # Who
    location: str    # Where
    timestamp: str   # When
    action: str      # What

memory.create_lookup("by_character", lambda x: x.char_name)
memory.create_lookup("by_location", lambda x: x.location)
memory.create_lookup("by_hour", lambda x: x.timestamp.split(':')[0])

# Find all events involving a character
character_history = memory.get_by_lookup("by_character", "Alice")

# Find all events in a location
location_events = memory.get_by_lookup("by_location", "Kitchen")

# Find all events in morning hours (08:00-09:00, etc.)
morning_events = memory.get_by_lookup("by_hour", "08")
```

### 2. User Profile Management

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

# Fast lookups
user = memory.get_by_lookup("by_email", "alice@example.com")[0]
company_users = memory.get_by_lookup("by_company", "TechCorp")
dept_users = memory.get_by_lookup("by_department", "TechCorp:Engineering")
```

### 3. Hierarchical Data

```python
# Composite keys for hierarchical queries
memory.create_lookup(
    "by_location_hour",
    lambda x: f"{x.location}:{x.timestamp.split(':')[0]}"
)

# Query: Kitchen events during 08:00
results = memory.get_by_lookup("by_location_hour", "Kitchen:08")
```

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Create lookup | O(n) | One-time cost (n = existing items) |
| Query | **O(1)** | Hash lookup |
| Retrieve matches | O(m) | m = number of matching items |
| Add item | O(l) | l = number of lookups |
| Remove item | O(l) | Cleanup on all lookups |
| Merge item | O(l) | Remove old + add new for each lookup |

### Memory Overhead

Lookups store only references (primary keys), minimizing memory:

```
Scenario: 1,000,000 items, 10 lookups, 100 unique values per lookup
Memory: ~4-10 MB (0.001-0.01% of storage)
```

Compare this to vector indices which typically consume 10-50% of storage.

## Best Practices

### ✅ Do

- Create lookups **before** adding large amounts of data
- Use lookups for **exact matching** on specific fields
- Combine lookups with vector search for powerful queries
- Drop unused lookups to save memory
- Use hashable types for lookup keys (str, int, tuple)

### ❌ Don't

- Use lookups for fuzzy/partial matching (use vector search instead)
- Create lookups for every possible field (be selective)
- Store `None` values in lookups (they're skipped with warnings)
- Rely on lookups for substring matching (not supported)

## Combining Lookups with Vector Search

Get the best of both worlds:

```python
# Step 1: Precise filtering with Lookups
kitchen_events = memory.get_by_lookup("by_location", "Kitchen")

# Step 2: Semantic search on filtered results
relevant_kitchen_events = [
    e for e in kitchen_events 
    if e in memory.search("cooking activities", top_k=100)
]

# Or vice versa
relevant_in_memory = memory.search("cooking", top_k=50)
kitchen_relevant = [
    e for e in relevant_in_memory
    if e in memory.get_by_lookup("by_location", "Kitchen")
]
```

## Troubleshooting

### Q: "Lookup 'by_name' already exists"

A: You tried to create a lookup with a name that already exists. Use `drop_lookup()` first or use a different name.

```python
memory.drop_lookup("by_name")
memory.create_lookup("by_name", new_extractor)
```

### Q: My lookup returns empty results

A: Common causes:
1. **Typo in key**: Check the exact value being used
2. **Extractor mismatch**: Verify the extractor returns the value you're querying
3. **None values**: Some items might return `None` from the extractor

### Q: Lookups are not consistent after merge

This shouldn't happen. If it does, file an issue. Lookups are automatically updated on every merge.

## Migration Guide

If you were manually indexing before:

**Before:**
```python
# Manual index maintenance
name_index = {}
for item in memory.items:
    if item.name not in name_index:
        name_index[item.name] = []
    name_index[item.name].append(item)

# Manual query
alice = name_index.get("Alice", [])
```

**After:**
```python
# Automatic with Lookups
memory.create_lookup("by_name", lambda x: x.name)
alice = memory.get_by_lookup("by_name", "Alice")
```

The Lookups feature handles all maintenance automatically, including updates during merges and removals.

## See Also

- [Vector Search Guide](../basic-concepts.md) - Learn about semantic search with vector indices
- [Merge Strategies Guide](../user-guide/merge-strategies.md) - Understand how duplicate detection and merging works
- [API Reference](../api/core/overview.md) - Full OMem API documentation
