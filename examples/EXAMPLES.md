# OMem Examples - Quick Reference

## 5 Practical Examples Summary

| # | Name | Theme | Strategy | Lines | Complexity |
|---|------|-------|----------|-------|-----------|
| 01 | Self-Improving Debugger | Error Learning | LLM.BALANCED | 176 | ⭐⭐⭐ |
| 02 | RPG NPC Memory | Character Profiling | FIELD_MERGE | 176 | ⭐⭐ |
| 03 | Semantic Scholar | Research Library | Vector Search | 218 | ⭐⭐⭐ |
| 04 | Multi-Source Fusion | Data Integration | LLM.BALANCED | 252 | ⭐⭐⭐⭐ |
| 05 | Conversation History | Chat Memory | FIELD_MERGE | 250 | ⭐⭐⭐ |

## Feature Matrix

### Merge Strategies Used
- **FIELD_MERGE**: Examples 02, 05 (incremental field updates)
- **LLM.BALANCED**: Examples 01, 04 (intelligent consolidation)
- **Vector Search**: Example 03 (semantic similarity)

### Data Persistence
- **All examples** save to `temp/{example_name}/`
- `memory.json`: Consolidated items list
- `metadata.json`: Schema and statistics

### API Requirements
- **No API Key**: Examples 02, 05 ✅
- **Optional API Key**: Examples 01, 04 (gracefully fallback)
- **Requires API Key**: Example 03 (needs OpenAI embeddings)

### Example Sizes
```
01_self_improving_debugger.py  |████████ 6.1 KB
02_rpg_npc_memory.py           |████████ 6.5 KB
03_semantic_scholar.py         |██████████ 8.0 KB
04_multi_source_fusion.py      |███████████ 8.5 KB
05_conversation_history.py     |████████████ 9.7 KB
```

## Data Structures Overview

### Example 1: DebugLog
```python
error_id: str                      # Unique error identifier
error_type: str                    # Type of error
error_message: str                 # Error message
stack_trace: str | None            # Stack trace
solutions: list[str]               # Multiple solutions found
attempted_fixes: list[str]         # Fixes tried so far
root_cause: str | None             # Inferred root cause
```

### Example 2: NPCMemory
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

### Example 3: ResearchPaper
```python
paper_id: str                      # Paper unique ID
title: str                         # Paper title
authors: list[str]                 # Author names
abstract: str                      # Paper abstract
year: int                          # Publication year
citations: int                     # Citation count
keywords: list[str]                # Research keywords
related_papers: list[str]          # Related paper IDs
```

### Example 4: CustomerProfile
```python
customer_id: str                   # Customer ID
name: str | None                   # Customer name
email: str | None                  # Email address
phone: str | None                  # Phone number
company: str | None                # Company/Organization
job_title: str | None              # Job title
total_spending: float | None       # Lifetime spending
support_tickets: list[str]         # Support ticket IDs
preferred_products: list[str]      # Product preferences
communication_preferences: list    # Preferred channels
data_sources: list[str]            # Which systems provided data
last_updated: str | None           # Last update timestamp
```

### Example 5: ConversationMemory
```python
session_id: str                    # Conversation session ID
user_name: str | None              # User's name
known_topics: list[str]            # Discussed topics
user_preferences: list[str]        # Stated preferences
user_interests: list[str]          # Inferred interests
goals_discussed: list[str]         # User's goals
decisions_made: list[str]          # Agreed decisions
open_questions: list[str]          # Unanswered questions
context_notes: str | None          # Additional context
```

## Running Commands

```bash
# Test single example
python examples/01_self_improving_debugger.py

# Test all examples with timing
time for i in {1..5}; do python examples/0${i}_*.py > /dev/null 2>&1; done

# Check generated memory files
ls -la temp/*/memory.json

# View specific memory
cat temp/debugger_memory.json/memory.json | python -m json.tool | head -20
```

## Execution Flow for Each Example

### Example 1: Debugger
1. Create multiple error encounters (same error, different contexts)
2. Initialize OMem with LLM merge strategy
3. Add all encounters → LLM intelligently consolidates
4. Retrieve unified solutions
5. Persist to disk

### Example 2: NPC Memory
1. Create multiple NPC encounters with player
2. Initialize OMem with FIELD_MERGE strategy
3. Add all encounters → Field-level merging updates profile
4. Retrieve complete NPC memory of player
5. Generate NPC dialogue based on memory
6. Persist to disk

### Example 3: Scholar Library
1. Load research papers with metadata
2. Initialize OMem with embeddings (optional)
3. Add papers to library
4. Perform semantic search on abstracts
5. Display statistics and top keywords
6. Persist library and indices

### Example 4: Customer Fusion
1. Create customer records from 4 different sources
2. Initialize OMem with LLM merge strategy
3. Add all records → LLM resolves conflicts
4. Generate unified profile with data quality report
5. Show integration benefits
6. Persist to disk

### Example 5: Conversation
1. Simulate 4 turns of conversation
2. Initialize OMem with FIELD_MERGE strategy
3. Add all turns → Facts accumulate and refine
4. Generate AI response based on consolidated memory
5. Display memory statistics
6. Persist conversation history

## Key Takeaways

✅ **FIELD_MERGE** works best for incremental profile building
✅ **LLM.BALANCED** excels at resolving conflicts and reasoning
✅ **Vector Search** enables semantic discovery
✅ **All examples** demonstrate real-world use cases
✅ **English comments** make examples universally accessible
✅ **Graceful degradation** handles missing API keys

## Next Steps

1. Study how different strategies handle the same data
2. Try modifying the data to see different merge outcomes
3. Add custom extractors for your specific ID schemes
4. Combine patterns for more complex scenarios
5. Extend with your own use cases!
