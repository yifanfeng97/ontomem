# Merge Strategies Guide

Learn how to choose and implement the right merge strategy for your use case.

## Overview

OntoMem supports 7 merge strategies for handling conflicts when updating entities:

| Strategy | Category | Behavior | Use Case |
|----------|----------|----------|----------|
| `MERGE_FIELD` | Classic | Non-null overwrites, lists append | Default choice, simple scenarios |
| `KEEP_INCOMING` | Classic | Always use newest data | Status updates, current state |
| `KEEP_EXISTING` | Classic | Always keep first observation | Historical records, timestamps |
| `LLM.BALANCED` | LLM | Intelligently synthesize both | Complex contradictions |
| `LLM.PREFER_INCOMING` | LLM | Prefer new data when conflicting | New info should take priority |
| `LLM.PREFER_EXISTING` | LLM | Prefer existing data when conflicting | Old info should take priority |
| `LLM.CUSTOM_RULE` | LLM | User-defined logic with dynamic context | Advanced, domain-specific rules |

## Classic Strategies

### MERGE_FIELD (Default)

**Behavior**: Non-null fields overwrite, lists are appended.

```python
from ontomem import OMem, MergeStrategy

memory = OMem(
    memory_schema=Profile,
    key_extractor=lambda x: x.id,
    merge_strategy=MergeStrategy.MERGE_FIELD
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

## Custom Merge Rules

For advanced use cases where built-in strategies don't fit, you can define your own merge logic using `MergeStrategy.LLM.CUSTOM_RULE`. This allows you to provide natural language instructions and inject dynamic context at runtime.

### Parameters

- **`rule`** (str): A static instruction string describing how to handle conflicts. Written in natural language, it guides the LLM on your specific merge logic.
- **`dynamic_rule`** (Callable[[], str], optional): A function that returns a string at runtime. Useful for injecting time-based logic, environment variables, or agent state.

### Basic Example

```python
from ontomem.merger import create_merger, MergeStrategy

merger = create_merger(
    strategy=MergeStrategy.LLM.CUSTOM_RULE,
    key_extractor=lambda x: x.id,
    llm_client=llm,
    item_schema=UserProfile,
    rule="Merge profiles intelligently. If a conflict arises between existing and incoming data, prefer data from the GitHub source. Always keep the most complete bio description."
)

# Use in memory
memory = OMem(
    memory_schema=UserProfile,
    key_extractor=lambda x: x.id,
    merger=merger,
    llm_client=llm,
    embedder=embedder
)
```

### Dynamic Rules

Dynamic rules are evaluated at runtime, allowing your merge strategy to adapt based on context.

```python
from datetime import datetime

def get_time_aware_context():
    """Inject time-based logic into merge rules."""
    hour = datetime.now().hour
    if hour > 18:
        return "Current time: evening. Prefer recent updates as they are fresher."
    else:
        return "Current time: business hours. Prefer verified, stable data."

merger = create_merger(
    strategy=MergeStrategy.LLM.CUSTOM_RULE,
    key_extractor=lambda x: x.id,
    llm_client=llm,
    item_schema=UserProfile,
    rule="Intelligently merge user profiles. Prioritize recent email addresses and keep all unique skills.",
    dynamic_rule=get_time_aware_context
)
```

### Real-World Example: Environment-Aware Merging

```python
import os

def get_environment_rules():
    """Adjust merge rules based on deployment environment."""
    env = os.getenv("ENVIRONMENT", "dev")
    if env == "production":
        return "PRODUCTION MODE: Use conservative merge strategy. Only accept updates from verified sources. Keep existing data if in doubt."
    else:
        return "DEVELOPMENT MODE: Accept all incoming updates for faster iteration and testing."

merger = create_merger(
    strategy=MergeStrategy.LLM.CUSTOM_RULE,
    key_extractor=lambda x: x.id,
    llm_client=llm,
    item_schema=Company,
    rule="Merge company records by consolidating all unique information.",
    dynamic_rule=get_environment_rules
)
```

### Time-Series Consolidation Example

```python
from datetime import datetime

class DailyReport(BaseModel):
    employee_id: str
    date: str
    tasks_completed: int
    mood: str

def get_consolidation_context():
    """Adjust consolidation based on report timing."""
    now = datetime.now()
    day_name = now.strftime("%A")
    return f"Today is {day_name}. Mid-week reports should balance all tasks. End-of-week reports should summarize the whole week."

# Composite key: employee_id + date for daily consolidation
memory = OMem(
    memory_schema=DailyReport,
    key_extractor=lambda x: f"{x.employee_id}_{x.date}",
    merger=create_merger(
        strategy=MergeStrategy.LLM.CUSTOM_RULE,
        rule="Consolidate multiple daily updates into one coherent daily report. Sum task counts and synthesize mood description.",
        dynamic_rule=get_consolidation_context
    ),
    llm_client=llm
)
```

**When to use**:
- Complex, domain-specific merge logic
- Context-dependent merging (time, environment, state)
- Advanced data quality rules
- Multi-source reconciliation with specific priorities

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

# MERGE_FIELD
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

# LLM.CUSTOM_RULE
# Result: "7 years (evolved from 5)", all skills with custom logic applied
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
├─ Simple fields → MERGE_FIELD
└─ Complex relationships/contradictions → LLM.* strategies
```

### Quick Reference

- 🎯 **Default**: `MERGE_FIELD` - works for most cases
- ⚡ **Status updates**: `KEEP_INCOMING` - latest wins
- 📚 **Historical**: `KEEP_EXISTING` - first wins
- 🧠 **Complex logic**: `LLM.BALANCED` - intelligent synthesis
- 🔄 **Evolving data**: `LLM.PREFER_INCOMING` - new data takes precedence
- 🏛️ **Authoritative**: `LLM.PREFER_EXISTING` - original is truth
- ✨ **Custom rules**: `LLM.CUSTOM_RULE` - user-defined logic with runtime context

---

## Performance Considerations

| Strategy | Speed | Cost | Notes |
|----------|-------|------|-------|
| MERGE_FIELD | ⚡⚡⚡ | Free | No API calls |
| KEEP_INCOMING | ⚡⚡⚡ | Free | No API calls |
| KEEP_EXISTING | ⚡⚡⚡ | Free | No API calls |
| LLM.BALANCED | ⚡ | LLM tokens | ~500-1000 tokens per merge |
| LLM.PREFER_INCOMING | ⚡ | LLM tokens | ~500-1000 tokens per merge |
| LLM.PREFER_EXISTING | ⚡ | LLM tokens | ~500-1000 tokens per merge |
| LLM.CUSTOM_RULE | ⚡ | LLM tokens | ~500-1000 tokens per merge + dynamic_rule evaluation |

**Tip**: Use classic strategies for high-frequency updates, LLM strategies sparingly for important consolidations.

---

## Next Steps

- See [Examples](../examples/examples-overview.md) for real-world usage
- Explore [Advanced Usage](advanced-usage.md)
- Check [API Reference](../api/overview.md) for details

---

**Questions?** Check our [FAQ](../faq.md).
