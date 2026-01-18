# 02: RPG NPC Memory

## Overview

Simulates an RPG game where NPCs build their memory of player characters through multiple interactions. Each encounter adds or updates information about the player, demonstrating incremental profile building.

## Theme

**Character Profile Building**

## Strategy

**FIELD_MERGE** (incremental field updates)

## Key Features

- ✅ Multiple interaction types (trade, combat, dialogue)
- ✅ Field-level merging for profile completeness
- ✅ Progressive reputation and relationship tracking
- ✅ Incremental skill and achievement recognition
- ✅ Location-based memory tracking

## Data Structure

### NPCMemory
```python
player_id: str                     # Player unique ID
player_name: str | None            # Known player names
titles_earned: list[str]           # Achievements
reputation_events: list[str]       # Important events
known_skills: list[str]            # Discovered skills
trade_history: list[dict]          # Transaction history
first_meeting_location: str | None # First encounter place
last_known_location: str | None    # Last seen location
npc_opinion: str | None            # NPC's opinion of player
party_relationship: str | None     # Relationship status
```

## Use Case

**Game Development**: Building NPC memory systems that track player interactions, remember past events, and evolve relationships based on accumulated experiences.

**Benefits**:
- Realistic NPC memory of player interactions
- Dynamic relationship tracking
- Progressive skill discovery
- Persistent reputation system

## Running the Example

```bash
cd examples/
python 02_rpg_npc_memory.py
```

## Output

Results are stored in `temp/npc_memory/`:
- `memory.json`: NPC memory records for each player
- `metadata.json`: Schema and statistics

## What You'll Learn

1. **Incremental Updates**: How to progressively build profiles through multiple interactions
2. **Field-Level Merging**: Merging individual fields while preserving list information
3. **Relationship Tracking**: Maintaining evolving relationships and reputation
4. **Game State Integration**: Integrating OntoMem with game systems

## No API Required ✅

This example works without any external API keys or dependencies beyond the core OntoMem package.

## Related Concepts

- [Merge Strategies](../user-guide/merge-strategies.md)
- [Key Extraction](../user-guide/key-extraction.md)

## Next Examples

- [03: Semantic Scholar](03-semantic-scholar.md) - Vector search capabilities
- [05: Conversation History](05-conversation-history.md) - Similar profile building in dialogue
