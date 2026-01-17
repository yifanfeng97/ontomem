# Advanced Usage

Master advanced patterns and optimization techniques.

## Batch Operations

```python
# Add many items efficiently
researchers = [r1, r2, r3, ..., r1000]
memory.add(researchers)  # All merged in batch

# Query properties
print(memory.keys)   # All unique keys
print(memory.items)  # All entities
print(memory.size)   # Total count
```

## Custom Key Extractors

```python
# Composite keys
key_extractor = lambda x: f"{x.first_name}_{x.last_name}"

# Case-insensitive
key_extractor = lambda x: x.email.lower()

# Hash-based (for sensitive data)
import hashlib
key_extractor = lambda x: hashlib.md5(x.id.encode()).hexdigest()
```

## Incremental Indexing

```python
# First build
memory.build_index()

# Add new items - index auto-updates
memory.add(new_researcher)

# Manual rebuild if needed
memory.build_index(force=True)
```

## Memory Management

```python
# Check size
print(f"Memory contains {memory.size} entities")

# Clear if needed
memory.clear()  # Removes all data and indices

# Remove specific items
success = memory.remove("john_doe")
```

## Error Handling

```python
from ontomem import OMem, MergeStrategy

try:
    memory.add(item)
except Exception as e:
    print(f"Error: {e}")
    # Handle gracefully
```

---

See [API Reference](../api/overview.md) for more details.
