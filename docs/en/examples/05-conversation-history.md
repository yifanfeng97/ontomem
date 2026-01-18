# 05: Conversation History

## Overview

Shows how AI maintains and evolves its understanding of a user through multi-turn conversation. Each turn adds or refines knowledge, demonstrating incremental memory building in dialogue systems.

## Theme

**Conversational Memory Evolution**

## Strategy

**FIELD_MERGE with incremental fact accumulation**

## Key Features

- ✅ Turn-by-turn memory updates
- ✅ Incremental fact accumulation
- ✅ Automatic context maintenance
- ✅ Memory-aware response generation
- ✅ User preference tracking

## Data Structure

### ConversationMemory
```python
session_id: str                    # Conversation session ID
user_name: str | None              # User's name
known_topics: list[str]            # Discussed topics
user_preferences: list[str]        # Stated preferences
user_interests: list[str]          # Inferred interests
communication_style: str | None    # Preferred style
problem_history: list[str]         # Previous issues
solutions_applied: list[str]       # What's been tried
session_count: int                 # Number of sessions
last_interaction: str | None       # Last update time
```

## Use Case

**Conversational AI & Chatbots**: Build chatbots and dialogue systems that remember user preferences, track conversation history, and improve responses over time through accumulated knowledge.

**Benefits**:
- Personalized responses based on history
- Reduced need to re-explain context
- Progressive trust building
- Improved user experience

## Running the Example

```bash
cd examples/
python 05_conversation_history.py
```

## Output

Results are stored in `temp/conversation_memory/`:
- `memory.json`: Conversation memory records
- `metadata.json`: Schema and statistics

## No API Required ✅

This example works without any external API keys or dependencies beyond the core OntoMem package.

## What You'll Learn

1. **Multi-Turn Updates**: Updating memory across conversation turns
2. **Incremental Accumulation**: Building profiles gradually through dialogue
3. **Context Maintenance**: Keeping track of conversation context
4. **Preference Tracking**: Recording user preferences and interests
5. **Dialogue Integration**: Integrating OntoMem with chat systems

## Complexity

**⭐⭐⭐ Intermediate**: Shows practical dialogue system integration patterns.

## Related Concepts

- [Merge Strategies](../user-guide/merge-strategies.md)
- [Auto-Consolidation](../user-guide/auto-consolidation.md)
- [Persistence](../user-guide/persistence.md)

## Next Examples

- [02: RPG NPC Memory](02-rpg-npc-memory.md) - Similar profile building in gaming
- [06: Temporal Memory](06-temporal-memory-consolidation.md) - Time-based aggregation
