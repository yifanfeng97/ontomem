# Persistence

Save and restore your memory state.

## Saving Memory

Use `dump()` to save your entire memory state to disk:

```python
memory.dump("./my_memory")
```

This creates:
- `memory.json` - Your serialized entities
- `faiss_index/` - Vector index directory (if built)
- `metadata.json` - Configuration and metadata

## Loading Memory

Restore a saved memory state:

```python
# Create a new memory instance with same schema
new_memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.MERGE_FIELD
)

# Load saved state
new_memory.load("./my_memory")

# Your data is restored!
print(new_memory.size)  # Shows number of entities
```

## File Structure

```
my_memory/
├── memory.json           # Serialized entities
├── metadata.json         # Configuration and metadata
└── faiss_index/          # Vector index directory (if built)
    ├── index.faiss
    └── docstore.pkl
```

## Fine-grained Persistence (v0.1.5+)

For more control over what gets saved, use the granular methods:

### Save Only Data
```python
# Save just the structured data, no index or metadata
memory.dump_data("./my_data.json")
```

### Save Only Index
```python
# Save just the vector index
memory.dump_index("./my_index_folder")
```

### Save Only Metadata
```python
# Save just the metadata
memory.dump_metadata("./my_metadata.json")
```

### Load Only Data
```python
# Load just the structured data
new_memory.load_data("./my_data.json")
```

### Load Only Index
```python
# Load just the vector index
new_memory.load_index("./my_index_folder")
```

### Load Only Metadata
```python
# Load just the metadata
new_memory.load_metadata("./my_metadata.json")
```

### Selective Backup Strategy
```python
# Back up data and index separately
memory.dump_data("./backups/data_v1.json")
memory.dump_index("./backups/index_v1")

# Only restore data, rebuild index fresh
new_memory.load_data("./backups/data_v1.json")
new_memory.build_index()
```

## Backup & Recovery

```python
# Create timestamped backups
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
memory.dump(f"./backups/memory_{timestamp}")

# List and restore
import os
backups = os.listdir("./backups")
latest = sorted(backups)[-1]
memory.load(f"./backups/{latest}")
```

## Export to Standard Formats

```python
import json
import pandas as pd

# Export to JSON
with open("export.json", "w") as f:
    data = [item.model_dump() for item in memory.items]
    json.dump(data, f, indent=2)

# Export to CSV
df = pd.DataFrame([item.model_dump() for item in memory.items])
df.to_csv("export.csv", index=False)

# Export to Parquet (for large datasets)
df.to_parquet("export.parquet")
```

---

Next: Explore [Advanced Usage](advanced-usage.md).
