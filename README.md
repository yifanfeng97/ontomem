# 🧠 Ontomem: The Self-Consolidating Memory

<div align="center">

[中文版本](README_ZH.md) | English

</div>

**Ontomem** is built on the concept of *Ontology Memory*—structured, coherent knowledge representation for AI systems.

> **Give your AI agent a "coherent" memory, not just "fragmented" retrieval.**

<p align="center">
  <img src="docs/assets/fw.png" alt="Ontomem Framework Diagram" width="800" />
</p>

<div align="center">

<a href="https://pypi.org/project/ontomem/"><img src="https://img.shields.io/pypi/v/ontomem.svg" alt="PyPI version"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"></a>
<a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
<a href="https://pypi.org/project/ontomem/"><img src="https://img.shields.io/pypi/dm/ontomem.svg" alt="PyPI downloads"></a>

</div>

Traditional RAG (Retrieval-Augmented Generation) systems retrieve text fragments. **Ontomem** maintains **structured entities** using Pydantic schemas and intelligent merging algorithms.

It excels at **Time-Series Consolidation**: effortlessly merging streaming observations (like logs or chat turns) into coherent "Daily Snapshots" or "Session Summaries" simply by defining a composite key (e.g., `user_id + date`).

**It doesn't just store data—it continuously "digests" and "organizes" it.**

---

## ✨ Why Ontomem?

### 🧩 Schema-First & Type-Safe
Built on **Pydantic**. All memories are strongly-typed objects. Say goodbye to `{"unknown": "dict"}` hell and embrace IDE autocomplete and type checking.

### ⏱️ Temporal Consolidation (Time-Slicing)
Ontomem isn't just about ID deduplication. By using **Composite Keys** (e.g., `lambda x: f"{x.user}_{x.date}"`), you can automatically aggregate a day's worth of fragmented events into a **Single Daily Record**.
- **Input**: 1,000 fragmented logs/observations throughout the day.
- **Output**: 1 structured, LLM-synthesized "Daily Summary" object.

### 🔄 Auto-Evolution
When you insert new data about an existing entity, Ontomem doesn't create duplicates. It intelligently merges them into a **Golden Record** using configurable strategies (Conflict Resolution, List Appending, or **LLM-powered Synthesis**).

### 🔍 Hybrid Search
- **Key-Value Lookup**: O(1) exact access (e.g., "Get me Alice's summary for 2024-01-01").
- **Vector Search**: Semantic similarity search across your entire timeline (e.g., "When was Alice frustrated?").

### 💾 Stateful & Persistent
Save your complete memory state (structured data + vector indices) to disk and restore it in seconds on next startup.

---

## 🧠 Ontomem vs. Other Memory Systems

Most memory libraries store **Raw Text** or **Chat History**. Ontomem stores **Consolidated Knowledge**.

| Feature | **Ontomem** 🧠 | **Mem0** / Zep | **LangChain Memory** | **Vector DBs** (Pinecone/Chroma) |
| :--- | :--- | :--- | :--- | :--- |
| **Core Storage Unit** | ✅ **Structured Objects** (Pydantic) | Text Chunks + Metadata | Raw Chat Logs | Embedding Vectors |
| **Data "Digestion"** | ✅ **Auto-Consolidation & merging** | Simple Extraction | ❌ Append-only | ❌ Append-only |
| **Time Awareness** | ✅ **Time-Slicing** (Daily/Session Aggregation) | ❌ Timestamp metadata only | ❌ Sequential only | ❌ Metadata filtering only |
| **Conflict Resolution**| ✅ **LLM Logic** (Synthesize/Prioritize) | ❌ Last-write-wins | ❌ None | ❌ None |
| **Type Safety** | ✅ **Strict Schema** | ⚠️ Loose JSON | ❌ String only | ❌ None |
| **Ideal For** | **Long-term Agent Profiles, Knowledge Graphs** | Simple RAG, Search | Chatbots, Context Window | Semantic Search |

### 💡 The "Consolidation" Advantage

- **Traditional RAG**: Stores 50 chunks of "Alice likes apples", "Alice likes bananas". Search returns 50 fragments.
- **Ontomem**: Merges them into 1 object: `User(name="Alice", likes=["apples", "bananas"])`. Search returns **one complete truth**.

---

## 🚀 Quick Start

Build a structured memory store in 30 seconds.

### 1. Define & Initialize

```python
from pydantic import BaseModel
from ontomem import OMem

# 1. Define your memory schema
class UserProfile(BaseModel):
    name: str
    skills: list[str]
    last_seen: str

# 2. Initialize (Simple mode)
memory = OMem(
    memory_schema=UserProfile,
    key_extractor=lambda x: x.name  # Unique ID
)
```

### 2. Add & Merge (Auto-Consolidation)

Ontomem automatically merges data for the same ID.

```python
# First observation
memory.add(UserProfile(name="Alice", skills=["Python"], last_seen="10:00"))

# Later observation (New skill added, time updated)
memory.add(UserProfile(name="Alice", skills=["Docker"], last_seen="11:00"))

# Retrieve the consolidated "Golden Record"
alice = memory.get("Alice")
print(alice.skills)     # ['Python', 'Docker'] (Lists merged!)
print(alice.last_seen)  # "11:00" (Updated!)
```

### 3. Search & Retrieve

```python
# Exact retrieval
profile = memory.get("Alice")

# All keys in memory
all_keys = memory.keys

# Clear or remove
memory.remove("Alice")
```

---

## 💡 Advanced Examples

<details>
<summary><b>Example 1: The "Self-Improving" Debugger (Logic Evolution)</b></summary>

An AI agent that doesn't just store errors—it **synthesizes** debugging wisdom over time using `LLM.BALANCED` strategy.

```python
from ontomem import OMem, MergeStrategy
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class BugFixExperience(BaseModel):
    error_signature: str
    solutions: list[str]
    prevention_tips: str

memory = OMem(
    memory_schema=BugFixExperience,
    key_extractor=lambda x: x.error_signature,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)

# Day 1: Pip install
memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: pandas",
    solutions=["pip install pandas"],
    prevention_tips="Check requirements.txt"
))

# Day 2: Docker container (Different solution!)
memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: pandas",
    solutions=["apt-get install python3-pandas"],  # Added to list!
    prevention_tips="Use system packages in containers"  # LLM merges both tips
))

# Result: Single record with merged solutions + synthesized advice
guidance = memory.get("ModuleNotFoundError: pandas")
print(guidance.prevention_tips)
# >>> "In standard environments, check requirements.txt. 
#      In containerized environments, prefer system packages..."
```

</details>

<details>
<summary><b>Example 2: Temporal Memory & Daily Consolidation (Time-Series)</b></summary>

Turn a stream of fragmented events into a single "Daily Summary" record using **Composite Keys**.

```python
from ontomem import OMem, MergeStrategy

class DailyTrace(BaseModel):
    user: str
    date: str
    actions: list[str]  # Accumulates all day
    summary: str        # LLM synthesizes entire day

memory = OMem(
    memory_schema=DailyTrace,
    key_extractor=lambda x: f"{x.user}_{x.date}",  # <-- THE MAGIC KEY
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)

# 9:00 AM event
memory.add(DailyTrace(user="Alice", date="2024-01-01", actions=["Login"]))

# 5:00 PM event (Same day → Merges into SAME record)
memory.add(DailyTrace(user="Alice", date="2024-01-01", actions=["Logout"]))

# Next day (New date → NEW record)
memory.add(DailyTrace(user="Alice", date="2024-01-02", actions=["Login"]))

# Results:
# - alice_2024-01-01: actions=["Login", "Logout"], summary="Active trading day..."
# - alice_2024-01-02: actions=["Login"], summary="Brief session..."

# Semantic search across time
results = memory.search("When was Alice frustrated?", k=1)
```

For a complete working example, see [examples/06_temporal_memory_consolidation.py](examples/06_temporal_memory_consolidation.py)

</details>

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
| `KEEP_INCOMING` | Latest data wins | Status updates (current role, last seen) |
| `KEEP_EXISTING` | First observation stays | Historical records (first publication year) |
| `LLM.BALANCED` | **LLM-driven semantic merging** | Complex synthesis, contradiction resolution |
| `LLM.PREFER_INCOMING` | **LLM merges semantically, prefers new data on conflict** | New information should take priority when contradictions arise |
| `LLM.PREFER_EXISTING` | **LLM merges semantically, prefers existing data on conflict** | Existing data should take priority when contradictions arise |

```python
# Example: LLM intelligently merges conflicting information
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.LLM.BALANCED  # or LLM.PREFER_INCOMING, LLM.PREFER_EXISTING
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

## 🔧 Installation & Setup

### Basic Installation

```bash
pip install ontomem
```

Or with `uv`:
```bash
uv add ontomem
```

<details>
<summary><b>📦 For Developers</b></summary>

To set up the development environment with all testing and documentation tools:

```bash
uv sync --group dev
```

**Core Requirements:**
- Python 3.11+
- LangChain (for LLM integration)
- Pydantic (for schema definition)
- FAISS (for vector search)

</details>

---

## 👨‍💻 Author

**Yifan Feng** - [evanfeng97@gmail.com](mailto:evanfeng97@gmail.com)

---

## 🤝 Contributing

We're building the next generation of AI memory standards. PRs and issues welcome!

---

## 📝 License

Licensed under the Apache License, Version 2.0 - See [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software under the terms of the Apache License 2.0.

---

**Built with ❤️ for AI developers who believe memory is more than just search.**
