"""
OMem Examples - Practical Use Cases

This directory contains 7 comprehensive examples demonstrating different capabilities
and patterns of using OMem for intelligent memory consolidation.

**Available Languages:**
- 📝 English: Examples in this directory with English comments and output
- 🇨🇳 中文: Chinese translations in the `zh/` subdirectory

## Examples Overview

### 01_self_improving_debugger.py
**Theme**: Error Learning & Consolidation
**Strategy**: LLM.BALANCED merge with intelligent consolidation

Demonstrates how a debugging system learns from multiple error encounters.
Each time the same error is encountered, OMem consolidates previous experiences
using LLM-powered merging to generate better solutions.

**Key Features**:
- Multiple error encounters of the same type
- LLM-based intelligent merging of solutions
- Cross-encounter learning and synthesis
- Memory persistence for future debugging sessions

**Output**: Stored in `temp/debugger_memory.json`

---

### 02_rpg_npc_memory.py
**Theme**: Character Profile Building
**Strategy**: MERGE_FIELD (incremental field updates)

Simulates an RPG game where NPCs build their memory of player characters
through multiple interactions. Each encounter adds or updates information.

**Key Features**:
- Multiple interaction types (trade, combat, dialogue)
- Field-level merging for profile completeness
- Progressive reputation and relationship tracking
- Incremental skill and achievement recognition

**Output**: Stored in `temp/npc_memory.json`

---

### 03_semantic_scholar.py
**Theme**: Academic Paper Library
**Strategy**: Vector search + persistence

Builds a searchable research paper library with semantic search capabilities.
Papers can be discovered by content similarity, not just keywords.

**Key Features**:
- Vector embeddings for semantic search (requires OpenAI API key)
- Metadata management (citations, keywords, relationships)
- Library statistics and analysis
- Persistence of indexed papers

**Output**: Stored in `temp/scholar_library.json`

---

### 04_multi_source_fusion.py
**Theme**: Customer Data Integration
**Strategy**: LLM.BALANCED merge with conflict resolution

Consolidates customer information from multiple systems (CRM, billing,
support, marketing) into a unified profile using intelligent merging.

**Key Features**:
- Multi-system data integration
- Automatic conflict detection and resolution
- Data quality reporting and completeness tracking
- Lineage tracking (which systems contributed)

**Output**: Stored in `temp/customer_unified_profile.json`

---

### 05_conversation_history.py
**Theme**: Conversational Memory Evolution
**Strategy**: MERGE_FIELD with incremental fact accumulation

Shows how AI maintains and evolves its understanding of a user through
multi-turn conversation. Each turn adds or refines knowledge.

**Key Features**:
- Turn-by-turn memory updates
- Incremental fact accumulation
- Automatic context maintenance
- Memory-aware response generation

**Output**: Stored in `temp/conversation_memory.json`

---

### 07_lookups_demo.py
**Theme**: Multi-Dimensional Exact-Match Queries
**Strategy**: Lookups API (secondary indices)

Demonstrates how to use Lookups for O(1) fast queries across multiple dimensions
without vector search overhead. Perfect for scenarios where you need exact-match
filtering across different data attributes.

**Key Features**:
- Create custom indices on any data field
- O(1) lookup performance for precise queries
- Automatic consistency during merge operations
- Combine lookups with vector search for powerful queries
- Support for composite keys and complex indexing strategies

**Output**: Educational pseudo-code with 5 practical scenarios

---

## Running the Examples

All examples are self-contained and can be run directly:

```bash
# Run individual English examples
python examples/01_self_improving_debugger.py
python examples/02_rpg_npc_memory.py
python examples/03_semantic_scholar.py
python examples/04_multi_source_fusion.py
python examples/05_conversation_history.py
python examples/07_lookups_demo.py

# Run individual Chinese examples
python examples/zh/01_self_improving_debugger.py
python examples/zh/02_rpg_npc_memory.py
python examples/zh/03_semantic_scholar.py
python examples/zh/04_multi_source_fusion.py
python examples/zh/05_conversation_history.py
python examples/zh/07_lookups_demo.py

# Run all English examples
for i in {1..5..1} {7}; do python examples/0${i}_*.py; done

# Run all Chinese examples
for file in examples/zh/*.py; do python "$file"; done
```

For more information about the Chinese examples, see [examples/zh/README.md](zh/README.md).

## Environment Setup

Most examples work without additional setup. However, some features require OpenAI API:

1. **Debugger Example**: Uses LLM if available, falls back to field merge
2. **Semantic Scholar**: Requires `OPENAI_API_KEY` for semantic search
3. **Multi-Source Fusion**: Uses LLM if available, falls back to field merge

Set up your environment:

```bash
# Add OPENAI_API_KEY to .env
echo "OPENAI_API_KEY=sk-..." > ../.env
```

## Memory Output

Each example generates output stored in the `temp/` directory:

```
temp/
├── debugger_memory.json/          # Error consolidation memory
├── npc_memory.json/               # NPC character profile
├── scholar_library.json/          # Research paper library
├── customer_unified_profile.json/ # Customer data integration
└── conversation_memory.json/      # Conversation history
```

Each directory contains:
- `memory.json`: The consolidated memory data (list of items)
- `metadata.json`: Schema information and size metadata

## Key Patterns

### Pattern 1: Field-Level Merging
Used when you want to incrementally build profiles by updating individual fields.

### Pattern 2: LLM-Powered Merging
Used when you need intelligent consolidation that reasons about conflicting data.

### Pattern 3: Vector Search + Persistence
Used when you need semantic search capabilities with persistent storage.

### Pattern 4: Multi-System Integration
Used when combining data from heterogeneous sources with potential conflicts.

### Pattern 5: Conversational Evolution
Used when maintaining user context through multi-turn interactions.

## Customization

Feel free to extend these examples:

1. **Add more test data**: Modify the data arrays at the beginning
2. **Change merge strategies**: Try different MergeStrategy values
3. **Extend Pydantic models**: Add more fields to track additional information
4. **Custom extractors**: Modify key_extractor functions for different ID schemes
5. **Implement feedback loops**: Add user input to refine memory

## Notes

- All examples use English comments and output for clarity
- Data is persisted to `temp/` subdirectories for inspection
- Examples gracefully handle missing API keys by using field merge
- Debug logging shows the consolidation process (can be verbose)

## Further Reading

For more information on OMem capabilities, see:
- `README.md` - Project overview
- `README_ZH.md` - Chinese documentation
- `TESTING.md` - Test suite and features
"""
