# API Overview

Complete API reference for Ontomem.

## Core Class: OMem

The main class for managing your memory system.

### Constructor

```python
OMem(
    memory_schema: Type[T],
    key_extractor: Callable[[T], Any],
    llm_client: Optional[BaseChatModel] = None,
    embedder: Optional[Embeddings] = None,
    merge_strategy: MergeStrategy = MergeStrategy.FIELD_MERGE
)
```

**Parameters:**

- `memory_schema` (Type[T]): Pydantic model defining entity structure
- `key_extractor` (Callable): Function to extract unique key from entity
- `llm_client` (Optional): LangChain chat model for LLM strategies
- `embedder` (Optional): LangChain embeddings for semantic search
- `merge_strategy` (MergeStrategy): How to handle conflicts

### Core Methods

#### `add(items)`
Add one or more items to memory. Automatically merges duplicates.

```python
memory.add(researcher)  # Single item
memory.add([r1, r2, r3])  # Multiple items
```

#### `get(key)`
Retrieve an entity by its unique key.

```python
researcher = memory.get("Yann LeCun")
```

**Returns:** Entity or None if not found.

#### `remove(key)`
Remove an entity by key.

```python
success = memory.remove("Yann LeCun")
```

**Returns:** bool - True if removed, False if not found.

#### `clear()`
Remove all entities and reset indices.

```python
memory.clear()
```

#### `build_index()`
Build or rebuild the vector index for semantic search.

```python
memory.build_index()  # Build from scratch
memory.build_index(force=True)  # Force rebuild
```

#### `search(query, k=5)`
Semantic search over entities.

```python
results = memory.search("deep learning neural networks", k=10)
```

**Parameters:**
- `query` (str): Natural language search query
- `k` (int): Number of results

**Returns:** List of top-k entities by semantic similarity

#### `dump(folder_path)`
Save memory state to disk.

```python
memory.dump("./my_memory")
# Creates: my_memory/memory.json, my_memory/faiss.index, etc.
```

#### `load(folder_path)`
Load memory state from disk.

```python
memory.load("./my_memory")
```

### Properties

#### `keys`
Get all unique keys in memory.

```python
all_keys = memory.keys  # List[Any]
```

#### `items`
Get all entity instances.

```python
all_entities = memory.items  # List[T]
```

#### `size`
Get count of entities.

```python
count = memory.size  # int
```

---

## Enumerations

### MergeStrategy

```python
from ontomem import MergeStrategy

class MergeStrategy(Enum):
    FIELD_MERGE = "field_merge"
    KEEP_INCOMING = "keep_incoming"
    KEEP_EXISTING = "keep_existing"
    
    class LLM(Enum):
        BALANCED = "llm_balanced"
        PREFER_INCOMING = "llm_prefer_incoming"
        PREFER_EXISTING = "llm_prefer_existing"
```

---

## Type Hints

### Generic Type T

All entities must be Pydantic models:

```python
from pydantic import BaseModel

class Profile(BaseModel):
    id: str
    name: str
    age: int
```

### Optional Types

For optional dependency features:

```python
from typing import Optional
from ontomem import OMem

# LLM strategies optional if not using them
llm_client: Optional[ChatModel] = None
embedder: Optional[Embeddings] = None
```

---

## Error Handling

### Common Exceptions

```python
from ontomem import OMem, MergeStrategy

# KeyError: Key not found
try:
    entity = memory.get("nonexistent")
except KeyError:
    print("Entity not found")

# ValueError: Invalid strategy
try:
    memory = OMem(..., merge_strategy="invalid")
except ValueError:
    print("Invalid strategy")

# RuntimeError: LLM not configured
try:
    memory.add(entity)  # With LLM.BALANCED strategy but no llm_client
except RuntimeError:
    print("LLM client not configured")
```

---

## Examples

### Basic Usage

```python
from ontomem import OMem, MergeStrategy
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings

class Researcher(BaseModel):
    name: str
    institution: str
    papers: list[str]

memory = OMem(
    memory_schema=Researcher,
    key_extractor=lambda x: x.name,
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.FIELD_MERGE
)

memory.add(Researcher(
    name="Yann LeCun",
    institution="Meta AI",
    papers=["CNNs"]
))

researcher = memory.get("Yann LeCun")
print(researcher.papers)
```

### With LLM Merging

```python
from langchain_openai import ChatOpenAI

memory = OMem(
    memory_schema=Researcher,
    key_extractor=lambda x: x.name,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)
```

---

## Version Information

Check version:

```python
import ontomem
print(ontomem.__version__)  # e.g., "0.1.0"
```

---

See detailed guides:

- [Merge Strategies](../../user-guide/merge-strategies.md)
- [Advanced Usage](../../user-guide/advanced-usage.md)
- [Examples](../../examples/examples-overview.md)
