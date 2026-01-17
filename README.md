# 🧠 Ontomem: The Self-Consolidating Memory Layer

[中文版本](README_ZH.md) | English

**Ontomem** is built on the concept of *Ontology Memory*—structured, coherent knowledge representation for AI systems.

> **Give your AI agent a "coherent" memory, not just "fragmented" retrieval.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Traditional RAG (Retrieval-Augmented Generation) systems retrieve text fragments. **Ontomem** maintains **structured entities** using Pydantic schemas and intelligent merging algorithms. It automatically consolidates fragmented observations into complete knowledge graph nodes.

**It doesn't just store data—it continuously "digests" and "organizes" it.**

---

## ✨ Why Ontomem?

### 🧩 Schema-First & Type-Safe
Built on **Pydantic**. All memories are strongly-typed objects. Say goodbye to `{"unknown": "dict"}` hell and embrace IDE autocomplete and type checking.

### 🔄 Auto-Consolidation
When you insert different pieces of information about the same entity (same ID) multiple times, Ontomem doesn't create duplicates. It intelligently merges them into a **Golden Record** using configurable strategies (field overrides, list merging, or **LLM-powered intelligent fusion**).

### 🔍 Hybrid Search
- **Key-Value Lookup**: O(1) exact entity access
- **Vector Search**: Built-in FAISS indexing for semantic similarity search, automatically synced

### 💾 Stateful & Persistent
Save your complete memory state (structured data + vector indices) to disk and restore it in seconds on next startup.

---

## 🚀 Quick Start: Building a "Self-Improving" Experience Library

Imagine an AI coding agent that debugs issues. Without memory, it repeats the same trial-and-error process every time. With **Ontomem**, it builds a persistent **"Debugging Playbook"** that evolves with each new problem encountered.

### 1. Define Your Experience Schema

```python
from pydantic import BaseModel
from typing import List, Optional

class BugFixExperience(BaseModel):
    """A living record of debugging knowledge."""
    error_signature: str            # Key: e.g., "ModuleNotFoundError: pandas"
    root_causes: List[str]          # Different reasons this error can occur
    solutions: List[str]            # Multiple working solutions discovered
    prevention_tips: str            # Synthesized understanding of how to avoid it
    last_updated: Optional[str] = None
```

### 2. Initialize with LLM-Powered Merging

We use the `LLM.BALANCED` strategy so Ontomem doesn't just list solutions—it **synthesizes** them into coherent, actionable guidance.

```python
from ontomem import OMem, MergeStrategy
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

experience_memory = OMem(
    memory_schema=BugFixExperience,
    key_extractor=lambda x: x.error_signature,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)
```

### 3. The Agent Learns Over Time

#### Day 1: The First Encounter
The agent encounters `ModuleNotFoundError` for pandas and fixes it with `pip install`.

```python
# Experience 1: Initial observation
experience_memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: No module named 'pandas'",
    root_causes=["Missing library in environment"],
    solutions=["Run: pip install pandas"],
    prevention_tips="Always check requirements.txt before running code."
))
```

#### Day 2: New Context, Different Fix
The agent encounters the same error in a Docker container where pip fails, but `apt-get install python3-pandas` works.

```python
# Experience 2: Different context, same error
experience_memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: No module named 'pandas'",
    root_causes=["Package not in system Python", "Binary incompatibility with pip"],
    solutions=["Run: apt-get install python3-pandas", "Use system package manager in containers"],
    prevention_tips="In containerized environments, prefer system packages for compiled dependencies."
))
```

#### Day 3: Agent Seeks Wisdom
When a new agent instance encounters the same error, it queries the evolved knowledge base:

```python
# Retrieve consolidated wisdom
guidance = experience_memory.get("ModuleNotFoundError: No module named 'pandas'")

print("Root Causes:")
for cause in guidance.root_causes:
    print(f"  - {cause}")
# Output:
#   - Missing library in environment
#   - Package not in system Python
#   - Binary incompatibility with pip

print("\nSolutions:")
for i, solution in enumerate(guidance.solutions, 1):
    print(f"  {i}. {solution}")
# Output:
#   1. Run: pip install pandas (standard approach)
#   2. Run: apt-get install python3-pandas (for system Python)
#   3. Use system package manager in containers

print("\nPrevention Tips:")
print(guidance.prevention_tips)
# Output: "Check requirements.txt before running code. 
#         In containers, prefer system packages for compiled dependencies.
#         Consider using virtual environments to isolate dependencies."
```

#### Day 4: Semantic Search for Similar Problems
The agent doesn't remember the exact error, but can search by concept:

```python
# Semantic search: Find solutions for import-related issues
similar_issues = experience_memory.search(
    "Python module import failures dependency missing",
    k=5
)

print(f"Found {len(similar_issues)} related debugging experiences")
```

**The agent went from "trial and error" to "informed decision-making". No boilerplate. No manual consolidation. Just add experiences and let Ontomem synthesize wisdom.**

---

## 🔍 Semantic Search

Build an index and search by natural language:

```python
# Build vector index
memory.build_index()

# Semantic search
results = memory.search("Find researchers working on transformer models and attention mechanisms")

for researcher in results:
    print(f"- {researcher.name}: {researcher.research_interests}")
```

---

## 🛠️ Merge Strategies

Choose how to handle conflicts:

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `FIELD_MERGE` | Non-null overwrites, lists append | Simple attribute collection |
| `KEEP_NEW` | Latest data wins | Status updates (current role, last seen) |
| `KEEP_OLD` | First observation stays | Historical records (first publication year) |
| `LLM.BALANCED` | **LLM-driven semantic merging** | Complex synthesis, contradiction resolution |

```python
# Example: LLM intelligently merges conflicting bios
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.LLM.BALANCED
)
```

---

## 💾 Save & Load

Snapshot your entire memory state:

```python
# Save (structured data → memory.json, vectors → FAISS indices)
memory.dump("./researcher_knowledge")

# Later, restore instantly
new_memory = OMem(...)
new_memory.load("./researcher_knowledge")
```

---

## 📊 Ontomem vs Traditional Approaches

| Feature | Traditional Vector DB | Ontomem 🧠 |
|---------|----------------------|-----------|
| **Storage Unit** | Text chunks | **Structured Objects** |
| **Deduplication** | Manual or via embeddings | **Native, ID-based** |
| **Updates** | Append-only (creates dupes) | **Auto-merge (upsert)** |
| **Query Results** | Similar text fragments | **Complete entities** |
| **Type Safety** | ❌ None | ✅ **Pydantic** |
| **Indexing** | Manual sync needed | ✅ **Auto-synced** |

---

## 🎯 Use Cases

### 🤖 AI Research Assistant
Consolidate researcher profiles, papers, and citations from multiple sources.

### 👤 Personal Knowledge Graph
Build a living profile of contacts, their preferences, skills, and interaction history from conversations.

### 🏢 Enterprise Data Hub
Unify customer/employee records from CRM, email, support tickets, and social media.

### 🧠 AI Agent Long-Term Memory
An autonomous agent accumulates experiences and observations—Ontomem keeps them organized and searchable.

---

## 🔧 Installation

### Basic Installation

```bash
pip install ontomem
```

Or with `uv`:
```bash
uv add ontomem
```

### For Developers

To set up the development environment with all testing and documentation tools:

```bash
uv sync --group dev
```

**Core Requirements:**
- Python 3.11+
- LangChain (for LLM integration)
- Pydantic (for schema definition)
- FAISS (for vector search)

---

## 📚 API Reference

### Core Methods

#### `add(items: Union[T, List[T]]) → None`
Add item(s) to memory. Automatically merges duplicates by key.

```python
memory.add(ResearcherProfile(...))
memory.add([item1, item2, item3])
```

#### `get(key: Any) → Optional[T]`
Retrieve an entity by its unique key.

```python
researcher = memory.get("yann_lecun_001")
```

#### `build_index(force: bool = False) → None`
Build or rebuild the vector index for semantic search.

```python
memory.build_index()  # Build if clean
memory.build_index(force=True)  # Force rebuild
```

#### `search(query: str, k: int = 5) → List[T]`
Semantic search over all entities.

```python
results = memory.search("transformers and attention", k=10)
```

#### `dump(folder_path: Union[str, Path]) → None`
Save memory state (data + index) to disk.

```python
memory.dump("./my_memory")
```

#### `load(folder_path: Union[str, Path]) → None`
Load memory state from disk.

```python
memory.load("./my_memory")
```

#### `remove(key: Any) → bool`
Remove an entity by key.

```python
success = memory.remove("yann_lecun_001")
```

#### `clear() → None`
Clear all entities and indices.

```python
memory.clear()
```

### Properties

#### `keys: List[Any]`
All unique keys in memory.

#### `items: List[T]`
All entity instances.

#### `size: int`
Number of entities.

---

## 🤝 Contributing

We're building the next generation of AI memory standards. PRs and issues welcome!

---

## 📝 License

MIT License - See LICENSE file for details.

---

**Built with ❤️ for AI developers who believe memory is more than just search.**
