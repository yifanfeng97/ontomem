# 🧠 Ontomem: The Self-Consolidating Memory

**Ontomem** is built on the concept of *Ontology Memory*—structured, coherent knowledge representation for AI systems.

> **Give your AI agent a "coherent" memory, not just "fragmented" retrieval.**


<p align="center">
  <img src="../assets/fw.png" alt="Ontomem Framework Diagram" width="700" />
</p>

[![PyPI version](https://img.shields.io/pypi/v/ontomem.svg)](https://pypi.org/project/ontomem/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI downloads](https://img.shields.io/pypi/dm/ontomem.svg)](https://pypi.org/project/ontomem/)

Traditional RAG (Retrieval-Augmented Generation) systems retrieve text fragments. **Ontomem** maintains **structured entities** using Pydantic schemas and intelligent merging algorithms. It automatically consolidates fragmented observations into complete knowledge graph nodes.

**It doesn't just store data—it continuously "digests" and "organizes" it.**


---

## ✨ Key Features

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

## 🚀 Quick Example

```python
from ontomem import OMem, MergeStrategy
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Define your schema
class BugFixExperience(BaseModel):
    error_signature: str
    solutions: list[str]
    prevention_tips: str

# Initialize memory
memory = OMem(
    memory_schema=BugFixExperience,
    key_extractor=lambda x: x.error_signature,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)

# Add experiences
memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: pandas",
    solutions=["pip install pandas"],
    prevention_tips="Check requirements.txt"
))

# Query
experience = memory.get("ModuleNotFoundError: pandas")
print(experience.solutions)  # Auto-merged across all observations!
```

---

## 📊 Why Ontomem?

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

## 🔗 Next Steps

- **[Getting Started](en/quick-start.md)** - 5-minute setup guide
- **[Merge Strategies](en/user-guide/merge-strategies.md)** - Learn about different merging approaches
- **[API Reference](en/api/overview.md)** - Complete API documentation

---

**Built with ❤️ for AI developers who believe memory is more than just search.**
