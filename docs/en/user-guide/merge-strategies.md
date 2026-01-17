# Merge Strategies Guide

Learn how to choose and implement the right merge strategy for your use case.

## Overview

Ontomem supports 6 merge strategies for handling conflicts when updating entities:

| Strategy | Category | Behavior | Use Case |
|----------|----------|----------|----------|
| `FIELD_MERGE` | Classic | Non-null overwrites, lists append | Default choice, simple scenarios |
| `KEEP_INCOMING` | Classic | Always use newest data | Status updates, current state |
| `KEEP_EXISTING` | Classic | Always keep first observation | Historical records, timestamps |
| `LLM.BALANCED` | LLM | Intelligently synthesize both | Complex contradictions |
| `LLM.PREFER_INCOMING` | LLM | Prefer new data when conflicting | New info should take priority |
| `LLM.PREFER_EXISTING` | LLM | Prefer existing data when conflicting | Old info should take priority |

## Classic Strategies

### FIELD_MERGE (Default)

**Behavior**: Non-null fields overwrite, lists are appended.

```python
from ontomem import OMem, MergeStrategy

memory = OMem(
    memory_schema=Profile,
    key_extractor=lambda x: x.id,
    merge_strategy=MergeStrategy.FIELD_MERGE
)

# Day 1
memory.add(Profile(
    id="user1",
    name="Alice",
    interests=["AI", "ML"]
))

# Day 2: Merge operation
memory.add(Profile(
    id="user1",
    name="Alice Johnson",  # Non-null: overwrites "Alice"
    interests=["NLP"]       # Lists: appended to ["AI", "ML"]
))

result = memory.get("user1")
# Result: name="Alice Johnson", interests=["AI", "ML", "NLP"]
```

**When to use**: Default choice for most scenarios.

---

### KEEP_INCOMING

**Behavior**: Always use the incoming (latest) data.

```python
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.KEEP_INCOMING
)

# Day 1: Initial status
memory.add(Profile(
    user_id="user1",
    status="offline",
    last_seen="2024-01-01"
))

# Day 2: User is now online
memory.add(Profile(
    user_id="user1",
    status="online",  # Will override
    last_seen="2024-01-15"  # Will override
))

result = memory.get("user1")
# Result: status="online", last_seen="2024-01-15"
```

**When to use**:
- User presence tracking
- Real-time status updates
- Current location/role
- Latest sensor readings

---

### KEEP_EXISTING

**Behavior**: Always preserve the first observation.

```python
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.KEEP_EXISTING
)

# Day 1: First publication
memory.add(Paper(
    doi="10.1234/example",
    title="Original Title",
    year=2020
))

# Day 5: Try to update (will be ignored)
memory.add(Paper(
    doi="10.1234/example",
    title="Updated Title",
    year=2024
))

result = memory.get("10.1234/example")
# Result: title="Original Title", year=2020 (unchanged)
```

**When to use**:
- First publication date (never changes)
- First observation timestamp
- Original name/identifier
- Historical records

---

## LLM-Powered Strategies

LLM strategies use an LLM client to **intelligently synthesize** conflicting information.

### Setup

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

memory = OMem(
    memory_schema=Profile,
    key_extractor=lambda x: x.id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)
```

### LLM.BALANCED

**Behavior**: LLM synthesizes both observations into a coherent, unified record.

```python
# Conflicting information about a researcher
memory.add(ResearcherProfile(
    name="John Smith",
    affiliation="University A",
    research_focus="Computer Vision"
))

# Later update with different info
memory.add(ResearcherProfile(
    name="John Smith",
    affiliation="University B",  # Conflict!
    research_focus="Machine Learning"  # Conflict!
))

# LLM synthesizes:
result = memory.get("John Smith")
# Result might be:
# {
#   "affiliation": "University A (moved to University B in 2023)",
#   "research_focus": "Computer Vision and Machine Learning",
#   "note": "Researcher transitioned focus from CV to broader ML"
# }
```

**When to use**: Complex, multi-faceted data requiring nuanced merging.

---

### LLM.PREFER_INCOMING

**Behavior**: LLM merges semantically, but **prefers new data** when conflicts arise.

```python
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.LLM.PREFER_INCOMING
)

# Original observation
memory.add(Company(
    name="TechCorp",
    description="A software company",
    ceo="John Doe"
))

# Updated information
memory.add(Company(
    name="TechCorp",
    description="A leading AI/ML solutions provider",  # New info
    ceo="Jane Smith"  # New CEO
))

# LLM synthesizes but prefers incoming:
result = memory.get("TechCorp")
# Result prefers: "Jane Smith" as CEO, updated description
```

**When to use**:
- Entities that evolve over time
- Where new information should typically override
- Role changes, technology pivots
- Current vs historical context

---

### LLM.PREFER_EXISTING

**Behavior**: LLM merges semantically, but **prefers existing data** when conflicts arise.

```python
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.LLM.PREFER_EXISTING
)

# First observation (authoritative)
memory.add(Person(
    name="Albert Einstein",
    birth_year=1879,
    field="Physics"
))

# Later conflicting update
memory.add(Person(
    name="Albert Einstein",
    birth_year=1880,  # Wrong!
    field="Physics and Philosophy"
))

# LLM synthesizes but prefers existing:
result = memory.get("Albert Einstein")
# Result keeps: birth_year=1879, uses authoritative first record
```

**When to use**:
- Biographical data (birth year, original name)
- First recorded observation is most reliable
- Scientific facts
- Immutable historical records

---

## Strategy Comparison

```python
# Same scenario with different strategies:

profile_v1 = Profile(
    id="alice",
    experience_years=5,
    skills=["Python", "ML"]
)

profile_v2 = Profile(
    id="alice",
    experience_years=7,  # Conflict
    skills=["Python", "ML", "DevOps"]
)

# FIELD_MERGE
# Result: experience_years=7, skills=["Python", "ML", "DevOps"]

# KEEP_INCOMING
# Result: experience_years=7, skills=["Python", "ML", "DevOps"]

# KEEP_EXISTING
# Result: experience_years=5, skills=["Python", "ML"]

# LLM.BALANCED
# Result: "7 years (progressed from 5)", includes all skills with context

# LLM.PREFER_INCOMING
# Result: Prefers 7 years and new skills, may note progression

# LLM.PREFER_EXISTING
# Result: Keeps 5 years, but includes new DevOps skill context
```

## Choosing a Strategy

### Decision Tree

```
Does your data change over time?
├─ Yes, and NEW data is more accurate → KEEP_INCOMING or LLM.PREFER_INCOMING
├─ Yes, but OLD data is more accurate → KEEP_EXISTING or LLM.PREFER_EXISTING
├─ Yes, both matter equally → LLM.BALANCED
└─ No, never changes → KEEP_EXISTING

Is your data complex/multi-faceted?
├─ Simple fields → FIELD_MERGE
└─ Complex relationships/contradictions → LLM.* strategies
```

### Quick Reference

- 🎯 **Default**: `FIELD_MERGE` - works for most cases
- ⚡ **Status updates**: `KEEP_INCOMING` - latest wins
- 📚 **Historical**: `KEEP_EXISTING` - first wins
- 🧠 **Complex logic**: `LLM.BALANCED` - intelligent synthesis
- 🔄 **Evolving data**: `LLM.PREFER_INCOMING` - new data takes precedence
- 🏛️ **Authoritative**: `LLM.PREFER_EXISTING` - original is truth

---

## Performance Considerations

| Strategy | Speed | Cost | Notes |
|----------|-------|------|-------|
| FIELD_MERGE | ⚡⚡⚡ | Free | No API calls |
| KEEP_INCOMING | ⚡⚡⚡ | Free | No API calls |
| KEEP_EXISTING | ⚡⚡⚡ | Free | No API calls |
| LLM.BALANCED | ⚡ | LLM tokens | ~500-1000 tokens per merge |
| LLM.PREFER_INCOMING | ⚡ | LLM tokens | ~500-1000 tokens per merge |
| LLM.PREFER_EXISTING | ⚡ | LLM tokens | ~500-1000 tokens per merge |

**Tip**: Use classic strategies for high-frequency updates, LLM strategies sparingly for important consolidations.

---

## Next Steps

- See [Examples](../examples/examples-overview.md) for real-world usage
- Explore [Advanced Usage](advanced-usage.md)
- Check [API Reference](../api/overview.md) for details

---

**Questions?** Check our [FAQ](../faq.md).
