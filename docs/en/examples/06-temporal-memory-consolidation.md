# 06: Temporal Memory Consolidation

## Overview

Turn a stream of fragmented events into a single "Daily Summary" record using **Composite Keys**. Demonstrates time-slicing aggregation where events throughout a day are consolidated into one coherent record with LLM-synthesized summaries.

## Theme

**Time-Series Data Aggregation**

## Strategy

**Time-Slicing with LLM.BALANCED merge**

## Key Features

- ✅ Daily aggregation of fragmented events
- ✅ Temporal bucketing using composite keys
- ✅ Time-aware consolidation
- ✅ LLM-synthesized daily summaries
- ✅ Trend analysis across time

## Data Structure

### DailyTrace
```python
user: str                          # User identifier
date: str                          # Date (YYYY-MM-DD)
actions: list[str]                 # Accumulated actions
summary: str                       # LLM-synthesized summary
mood: str | None                   # Inferred mood/sentiment
key_events: list[str]              # Important events
productivity: str | None           # Productivity assessment
notes: list[str]                   # Additional notes
```

## Use Case

**Analytics & Logging**: Consolidate streaming logs, user events, or telemetry into daily summaries. Useful for dashboards, analytics, and trend analysis across time periods.

**Benefits**:
- Reduced data volume (1 summary per day instead of 1000s of events)
- Better pattern recognition over time
- Efficient storage and retrieval
- Time-aware insights

## Running the Example

```bash
cd examples/

# Set your OpenAI API key for LLM synthesis (optional)
export OPENAI_API_KEY="your-key-here"

python 06_temporal_memory_consolidation.py
```

## Output

Results are stored in `temp/temporal_memory/`:
- `memory.json`: Daily summary records
- `metadata.json`: Schema and statistics
- `faiss_index/`: Vector index for temporal search

## API Requirements 🔄 Optional

This example works better with an **OpenAI API key** for LLM-powered synthesis, but can work without it for basic consolidation.

## What You'll Learn

1. **Composite Keys**: Using composite keys for time-aware grouping
2. **Time-Slicing**: Aggregating events into time buckets
3. **LLM Synthesis**: Generating summaries of events
4. **Temporal Patterns**: Discovering patterns across time
5. **Stream Processing**: Handling continuous event streams

## Complexity

**⭐⭐⭐ Intermediate**: Shows advanced time-aware consolidation patterns.

## Real-World Applications

- **Daily Activity Summaries**: Convert 1000s of user actions into daily digests
- **System Monitoring**: Aggregate logs into daily health reports
- **Analytics**: Convert event streams into analyzable daily metrics
- **Trend Analysis**: Identify patterns across days/weeks/months

## Related Concepts

- [Composite Keys](../user-guide/key-extraction.md#composite-keys)
- [Time-Series Data](../user-guide/advanced-usage.md#time-series)
- [Merge Strategies](../user-guide/merge-strategies.md)
- [Semantic Search](../user-guide/search-capabilities.md)

## Next Steps

- Explore [Advanced Usage](../user-guide/advanced-usage.md) for more patterns
- Learn about [Persistence](../user-guide/persistence.md)
- Check out [API Reference](../api/overview.md)
