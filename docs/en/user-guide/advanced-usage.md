# Advanced Usage

Master advanced patterns and optimization techniques.

## Batch Operations

```python
# Add many items efficiently
researchers = [r1, r2, r3, ..., r1000]
memory.add(researchers)  # All merged in batch

# Query properties
print(memory.keys)   # All unique keys
print(memory.items)  # All entities
print(memory.size)   # Total count
```

## Custom Key Extractors

```python
# Composite keys
key_extractor = lambda x: f"{x.first_name}_{x.last_name}"

# Case-insensitive
key_extractor = lambda x: x.email.lower()

# Hash-based (for sensitive data)
import hashlib
key_extractor = lambda x: hashlib.md5(x.id.encode()).hexdigest()
```

## Incremental Indexing

```python
# First build
memory.build_index()

# Add new items - index auto-updates
memory.add(new_researcher)

# Manual rebuild if needed
memory.build_index(force=True)
```

## Memory Management

```python
# Check size
print(f"Memory contains {memory.size} entities")

# Clear if needed
memory.clear()  # Removes all data and indices

# Remove specific items
success = memory.remove("john_doe")
```

## Error Handling

```python
from ontomem import OMem, MergeStrategy

try:
    memory.add(item)
except Exception as e:
    print(f"Error: {e}")
    # Handle gracefully
```

## Advanced: Custom Merge Rules with Dynamic Context

Create sophisticated merge strategies tailored to your domain using `MergeStrategy.LLM.CUSTOM_RULE`.

### Time-Aware Merging

```python
from datetime import datetime
from ontomem import OMem, MergeStrategy

# Define a function that adapts merge behavior based on time
def get_business_context():
    """Adjust merge strategy based on business hours."""
    hour = datetime.now().hour
    day = datetime.now().weekday()
    
    if day >= 5:  # Weekend
        return "Weekend mode: Accept all updates, prioritize user feedback over system logs"
    elif hour < 9 or hour > 17:  # After hours
        return "After-hours mode: Be conservative, prefer stable historical data"
    else:  # Business hours
        return "Business hours: Balance recent updates with verified historical data"

memory = OMem(
    memory_schema=UserActivity,
    key_extractor=lambda x: x.user_id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.CUSTOM_RULE,
    rule="""
    Merge user activity records:
    - Combine all unique actions into a timeline
    - Update user status based on most recent activity
    - Preserve all behavioral patterns and anomalies
    """,
    dynamic_rule=get_business_context
)
```

### Environment-Specific Logic

```python
import os

def get_environment_rules():
    """Adjust merge rules based on deployment environment."""
    env = os.getenv("ENVIRONMENT", "dev")
    
    if env == "production":
        return """
        PRODUCTION: Use strict merging.
        - Only accept verified data sources
        - Require evidence for conflicting information
        - Maintain data integrity above all
        """
    elif env == "staging":
        return """
        STAGING: Moderate merging.
        - Accept most updates with some validation
        - Log conflicts for debugging
        - Allow experimentation
        """
    else:  # dev
        return """
        DEVELOPMENT: Permissive merging.
        - Accept all incoming data
        - Fast iteration and testing
        - Log everything for inspection
        """

memory = OMem(
    memory_schema=SystemConfig,
    key_extractor=lambda x: x.config_id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.CUSTOM_RULE,
    rule="Intelligently merge system configuration updates",
    dynamic_rule=get_environment_rules
)
```

### State-Aware Multi-Source Consolidation

```python
class DataQualityState:
    """Track data quality metrics for context-aware merging."""
    def __init__(self):
        self.source_reliability = {
            "database": 0.95,
            "api": 0.85,
            "user_input": 0.60,
            "ml_inference": 0.75
        }

# Initialize state tracker
quality_state = DataQualityState()

def get_data_quality_rules():
    """Generate merge rules based on data source quality."""
    rules = "Merge data with quality weighting:\n"
    for source, reliability in quality_state.source_reliability.items():
        rules += f"- {source}: {reliability*100}% weight\n"
    rules += "Prefer high-quality sources in case of conflicts"
    return rules

memory = OMem(
    memory_schema=CustomerRecord,
    key_extractor=lambda x: x.customer_id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.CUSTOM_RULE,
    rule="Consolidate customer records from multiple sources",
    dynamic_rule=get_data_quality_rules
)

# As reliability changes, future merges adapt automatically
quality_state.source_reliability["user_input"] = 0.80  # User input improved
memory.add(new_customer_record)  # Uses updated quality weights
```

---

See [API Reference](../api/overview.md) for more details.
