# Examples Overview

Explore 6 real-world usage examples of OntoMem demonstrating different capabilities and use cases.

## Featured Examples

### 1️⃣ Self-Improving Debugger
An AI debugging agent that learns from each bug it encounters, building an evolving knowledge base of solutions.

**Theme**: Error Learning & Consolidation  
**Strategy**: LLM.BALANCED merge with intelligent consolidation  
**Key Features**: Error consolidation, LLM-powered merging, cross-encounter learning  
**[View Example →](01-self-improving-debugger.md)** | [Source Code](../../../examples/01_self_improving_debugger.py)

---

### 2️⃣ RPG NPC Memory
Simulates an RPG game where NPCs build their memory of player characters through multiple interactions.

**Theme**: Character Profile Building  
**Strategy**: FIELD_MERGE (incremental field updates)  
**Key Features**: Multiple interaction types, progressive reputation tracking, incremental skill recognition  
**[View Example →](02-rpg-npc-memory.md)** | [Source Code](../../../examples/02_rpg_npc_memory.py)

---

### 3️⃣ Semantic Scholar
Builds a searchable research paper library with semantic search capabilities. Papers can be discovered by content similarity, not just keywords.

**Theme**: Academic Paper Library  
**Strategy**: Vector search + persistence  
**Key Features**: Vector embeddings, semantic search (requires OpenAI API), metadata management  
**[View Example →](03-semantic-scholar.md)** | [Source Code](../../../examples/03_semantic_scholar.py)

---

### 4️⃣ Multi-Source Fusion
Consolidates customer information from multiple systems (CRM, billing, support, marketing) into a unified profile using intelligent merging.

**Theme**: Customer Data Integration  
**Strategy**: LLM.BALANCED merge with conflict resolution  
**Key Features**: Multi-system integration, automatic conflict resolution, data quality reporting, lineage tracking  
**[View Example →](04-multi-source-fusion.md)** | [Source Code](../../../examples/04_multi_source_fusion.py)

---

### 5️⃣ Conversation History
Shows how AI maintains and evolves its understanding of a user through multi-turn conversation.

**Theme**: Conversational Memory Evolution  
**Strategy**: FIELD_MERGE with incremental fact accumulation  
**Key Features**: Turn-by-turn updates, incremental fact accumulation, context maintenance  
**[View Example →](05-conversation-history.md)** | [Source Code](../../../examples/05_conversation_history.py)

---

### 6️⃣ Temporal Memory Consolidation
Turn a stream of fragmented events into a single "Daily Summary" record using **Composite Keys**.

**Theme**: Time-Series Data Aggregation  
**Strategy**: Time-Slicing with LLM.BALANCED merge  
**Key Features**: Daily aggregation, temporal bucketing, time-aware consolidation  
**[View Example →](06-temporal-memory-consolidation.md)** | [Source Code](../../../examples/06_temporal_memory_consolidation.py)

---

## Running the Examples

All examples are included in the `examples/` directory:

```bash
# Navigate to examples directory
cd examples/

# Run a specific example
python 01_self_improving_debugger.py
python 02_rpg_npc_memory.py
python 03_semantic_scholar.py
python 04_multi_source_fusion.py
python 05_conversation_history.py
python 06_temporal_memory_consolidation.py

# For Chinese versions
cd zh/
python 01_self_improving_debugger.py
```

---

## Feature Matrix

| # | Example | Theme | Strategy | Complexity | API Required |
|---|---------|-------|----------|-----------|--------------|
| 01 | Self-Improving Debugger | Error Learning | LLM.BALANCED | ⭐⭐⭐ | Optional |
| 02 | RPG NPC Memory | Character Profiling | FIELD_MERGE | ⭐⭐ | ❌ No |
| 03 | Semantic Scholar | Research Library | Vector Search | ⭐⭐⭐ | ✅ Yes |
| 04 | Multi-Source Fusion | Data Integration | LLM.BALANCED | ⭐⭐⭐⭐ | Optional |
| 05 | Conversation History | Chat Memory | FIELD_MERGE | ⭐⭐⭐ | ❌ No |
| 06 | Temporal Memory | Time-Series | LLM.BALANCED | ⭐⭐⭐ | Optional |

---

## Quick Start Examples

Check the [Quick Start](../quick-start.md) guide for immediate usage examples.

---

## Next Steps

- Explore the [API Reference](../api/overview.md)
- Read about [Merge Strategies](../user-guide/merge-strategies.md)
- Check the [FAQ](../faq.md)

