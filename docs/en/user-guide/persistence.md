# Persistence

Save and restore your memory state.

## Saving Memory

Use `dump()` to save your entire memory state to disk:

```python
memory.dump("./my_memory")
```

This creates:
- `memory.json` - Your serialized entities
- `faiss.index` - Vector index (if built)
- `metadata.json` - Configuration and timestamps

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
├── memory.json       # Serialized entities
├── faiss.index       # FAISS vector index
└── metadata.json     # Configuration
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
