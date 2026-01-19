# FAQ - Frequently Asked Questions

## Installation & Setup

### Q: What are the system requirements?

**A:** OntoMem requires:
- Python 3.11 or higher
- 2GB RAM minimum
- Any OS: Linux, macOS, or Windows

### Q: Do I need to install FAISS separately?

**A:** No, FAISS is included in the base installation (`faiss-cpu`). 

For GPU acceleration (NVIDIA only):
```bash
pip install faiss-gpu
```

### Q: Can I use OntoMem without LLM features?

**A:** Yes! LLM features are optional. You can use classic merge strategies (MERGE_FIELD, KEEP_INCOMING, KEEP_EXISTING) without any LLM client or embedder.

---

## Usage Questions

### Q: How do I define my data schema?

**A:** Use Pydantic BaseModel:

```python
from pydantic import BaseModel
from typing import List, Optional

class MyEntity(BaseModel):
    id: str  # Unique identifier
    name: str
    tags: List[str]
    metadata: Optional[dict] = None
```

### Q: What should I use as the key_extractor?

**A:** Any field (or combination) that uniquely identifies entities:

```python
# Simple: Use a single field
key_extractor=lambda x: x.id

# Composite: Combine multiple fields
key_extractor=lambda x: f"{x.first_name}_{x.last_name}"

# Complex: Custom logic
key_extractor=lambda x: x.email.lower().split("@")[0]
```

### Q: How does auto-merging work?

**A:** When you add an entity with an existing key:

1. **Merge** is triggered (doesn't create duplicate)
2. **Strategy** determines how conflicts are resolved
3. **Result** is a single consolidated entity

```python
memory.add(v1)  # Adds
memory.add(v1_updated)  # Triggers merge, doesn't duplicate
```

### Q: What's the difference between MERGE_FIELD and LLM.BALANCED?

**A:**

- **MERGE_FIELD**: Simple, deterministic (non-null overwrites)
- **LLM.BALANCED**: Intelligent synthesis, can resolve complex contradictions, slower and costs LLM tokens

Use MERGE_FIELD for speed/cost. Use LLM.BALANCED for complex data.

---

## Search & Retrieval

### Q: How do I search my memory?

**A:** Two methods:

```python
# 1. Exact lookup (fast)
entity = memory.get("john_doe")

# 2. Semantic search (requires index)
memory.build_index()
results = memory.search("artificial intelligence research", k=5)
```

### Q: Do I have to build an index to use memory?

**A:** No. You can use `get()` without building an index. Index is only needed for `search()`.

### Q: How many results should I retrieve with search()?

**A:** Depends on your use case:
- `k=1-5`: Find most relevant single item
- `k=5-10`: Get top candidates
- `k=20+`: Retrieve large candidate set

Start with `k=5` and adjust based on results.

---

## Persistence

### Q: How do I save my memory?

**A:** Use `dump()`:

```python
memory.dump("./my_memory")
# Creates: my_memory/memory.json, my_memory/faiss.index, etc.
```

### Q: How do I restore a saved memory?

**A:** Use `load()`:

```python
new_memory = OMem(...)  # Create instance with same schema
new_memory.load("./my_memory")  # Restore state
```

### Q: What files are created by dump()?

**A:**
- `memory.json`: Serialized entities
- `faiss.index`: Vector index (if built)
- `metadata.json`: Configuration info

### Q: Can I export memory to JSON/CSV?

**A:** Yes, manually:

```python
import json

# Export to JSON
with open("export.json", "w") as f:
    data = [item.model_dump() for item in memory.items]
    json.dump(data, f)

# Export to CSV
import pandas as pd
df = pd.DataFrame([item.model_dump() for item in memory.items])
df.to_csv("export.csv", index=False)
```

---

## Performance & Scaling

### Q: How many entities can OntoMem handle?

**A:** Depends on:
- Available RAM
- Entity size
- Search requirements

Guidelines:
- **<100K entities**: No issues
- **100K-1M entities**: Monitor RAM, consider batching
- **>1M entities**: Consider sharding or specialized vector DBs

### Q: Is semantic search slow?

**A:** No:
- Building index: ~0.5-1ms per entity
- Searching: ~10-100ms for typical queries
- Merging with MERGE_FIELD: <1ms
- Merging with LLM strategies: ~1-2 seconds (LLM call overhead)

### Q: Should I rebuild the index?

**A:** After major updates:
```python
memory.build_index(force=True)  # Rebuilds from scratch
```

Otherwise, it auto-updates incrementally.

---

## Integration & LLM

### Q: Which LLM providers are supported?

**A:** Any LangChain compatible model:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Open source (via Ollama, HuggingFace)

```python
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")

# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-opus")

# Ollama
from langchain_community.chat_models import ChatOllama
llm = ChatOllama(model="llama2")
```

### Q: How do I set my API key?

**A:**

```bash
# Environment variable
export OPENAI_API_KEY="sk-..."

# Or in code
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

### Q: Which embeddings model should I use?

**A:** Popular choices:

```python
from langchain_openai import OpenAIEmbeddings
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# Open source
from langchain_community.embeddings import HuggingFaceEmbeddings
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

---

## Troubleshooting

### Q: I get "ImportError: FAISS not found"

**A:**
```bash
pip install faiss-cpu
# or for GPU:
pip install faiss-gpu
```

### Q: LLM merge is very slow

**A:** This is expected. LLM calls take 1-2 seconds per merge. Use classic strategies for frequent operations.

### Q: My search results aren't relevant

**A:** Try:
1. Check embedding model (use better embeddings)
2. Increase `k` to get more candidates
3. Check search query quality

### Q: I'm getting duplicate entities

**A:** Verify `key_extractor` correctly identifies unique entities:

```python
# Check if keys are truly unique
keys = memory.keys
if len(keys) != len(set(keys)):
    print("Duplicate keys detected!")
```

### Q: Memory consumption is high

**A:** 
- Check entity size (use summarization if too large)
- Consider batching/sharding
- Rebuild index periodically

---

## Contributing & Development

### Q: How do I contribute to OntoMem?

**A:**
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit PR

See [Contributing](../contributing.md) guide.

### Q: How do I run tests?

**A:**
```bash
uv sync --group dev
pytest tests/
```

### Q: How do I build documentation?

**A:**
```bash
uv add --group dev mkdocs mkdocs-material
mkdocs serve
```

---

## Other Questions

### Q: Is OntoMem production-ready?

**A:** OntoMem is currently at version 0.1.4 (alpha). It's suitable for experimentation and development. Use in production with caution and thorough testing.

### Q: What's the roadmap?

**A:** Check [GitHub Issues](https://github.com/yifanfeng97/ontomem/issues) for planned features.

### Q: How do I report a bug?

**A:** Open an [issue on GitHub](https://github.com/yifanfeng97/ontomem/issues/new).

---

**Still have questions?** Ask on [GitHub Discussions](https://github.com/yifanfeng97/ontomem/discussions).
