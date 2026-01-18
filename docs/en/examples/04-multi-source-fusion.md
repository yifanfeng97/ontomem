# 04: Multi-Source Fusion

## Overview

Consolidates customer information from multiple systems (CRM, billing, support, marketing) into a unified profile using intelligent merging. Demonstrates advanced conflict resolution and data quality tracking across heterogeneous sources.

## Theme

**Customer Data Integration**

## Strategy

**LLM.BALANCED merge with conflict resolution**

## Key Features

- ✅ Multi-system data integration
- ✅ Automatic conflict detection and resolution
- ✅ Data quality reporting and completeness tracking
- ✅ Lineage tracking (which systems contributed)
- ✅ Unified customer view across departments

## Data Structure

### CustomerProfile
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

## Use Case

**Enterprise Data Management**: Unify customer data from CRM, billing, support, and marketing systems into a single golden record with intelligent conflict resolution.

**Benefits**:
- Single customer view across departments
- Reduced data silos
- Automatic conflict resolution
- Data quality improvements
- Better customer experiences

## Running the Example

```bash
cd examples/

# Set your OpenAI API key (optional, will fallback without it)
export OPENAI_API_KEY="your-key-here"

python 04_multi_source_fusion.py
```

## Output

Results are stored in `temp/customer_unified_profile/`:
- `memory.json`: Unified customer profiles
- `metadata.json`: Schema, statistics, and conflict logs

## API Requirements 🔄 Optional

This example works better with an **OpenAI API key** for intelligent conflict resolution, but has graceful fallback without it.

## What You'll Learn

1. **Multi-Source Integration**: Merging data from multiple heterogeneous sources
2. **Conflict Resolution**: Using LLM to intelligently resolve contradictions
3. **Data Quality**: Tracking completeness and quality metrics
4. **Lineage Tracking**: Recording which systems provided each piece of data
5. **Enterprise Patterns**: Building scalable data unification systems

## Complexity

**⭐⭐⭐⭐ Advanced**: This is the most complex example showing enterprise-level data integration patterns.

## Related Concepts

- [Merge Strategies](../user-guide/merge-strategies.md)
- [LLM Integration](../user-guide/llm-integration.md)
- [Conflict Resolution](../user-guide/merge-strategies.md#conflict-resolution)
- [Persistence](../user-guide/persistence.md)

## Next Examples

- [05: Conversation History](05-conversation-history.md) - Progressive profile building
- [06: Temporal Memory](06-temporal-memory-consolidation.md) - Time-aware aggregation
