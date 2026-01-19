# Quick Start

Get up and running with OntoMem in 5 minutes.

## Installation

### Using pip

```bash
pip install ontomem
```

### Using uv (recommended)

```bash
uv add ontomem
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yifanfeng97/ontomem.git
cd ontomem

# Install with dev dependencies
uv sync --group dev
```

## Your First Memory System

### Step 1: Define Your Schema

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ResearcherProfile(BaseModel):
    """A researcher's profile in your memory system."""
    name: str  # Will be the key
    affiliation: str
    research_interests: List[str]
    publications: List[str]
    last_updated: Optional[datetime] = None
```

### Step 2: Initialize OntoMem

```python
from ontomem import OMem, MergeStrategy
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Create memory instance
memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,  # Use name as unique key
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.MERGE_FIELD  # Start simple
)
```

### Step 3: Add Data

```python
# Add researcher profiles
memory.add(ResearcherProfile(
    name="Yann LeCun",
    affiliation="Meta AI",
    research_interests=["deep learning", "convolutional networks"],
    publications=["Backpropagation Applied to Handwritten Zip Code Recognition"]
))

memory.add(ResearcherProfile(
    name="Yoshua Bengio",
    affiliation="Mila",
    research_interests=["deep learning", "AI safety"],
    publications=["Learning Representations by Back-propagating Errors"]
))
```

### Step 4: Query

```python
# Get exact match
researcher = memory.get("Yann LeCun")
print(f"Found: {researcher.name}")
print(f"Interests: {researcher.research_interests}")
```

## Auto-Consolidation Example

Here's where OntoMem shines—automatic merging of fragmented data:

```python
# Day 1: You learn about Yann LeCun
memory.add(ResearcherProfile(
    name="Yann LeCun",
    affiliation="Meta AI",
    research_interests=["deep learning"],
    publications=["CNNs for Image Recognition"]
))

# Day 2: New information about the same person
memory.add(ResearcherProfile(
    name="Yann LeCun",
    affiliation="Meta AI",  # Same
    research_interests=["convolutional networks"],  # New detail
    publications=["Backpropagation Paper"]  # Additional paper
))

# Query the consolidated record
profile = memory.get("Yann LeCun")
print(profile.research_interests)
# Output: ["deep learning", "convolutional networks"]
# Output: ["CNNs for Image Recognition", "Backpropagation Paper"]
```

## Building an Index for Semantic Search

```python
# Build vector index
memory.build_index()

# Now search by semantic meaning
results = memory.search("machine learning neural networks", k=5)

for researcher in results:
    print(f"- {researcher.name}: {researcher.research_interests}")
```

## Save and Restore

```python
# Save entire memory state
memory.dump("./my_researcher_memory")

# Later, in a new Python session:
new_memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
)

# Restore
new_memory.load("./my_researcher_memory")

# Continue working
researcher = new_memory.get("Yann LeCun")
print(researcher.research_interests)  # Still there!
```

## Next Steps

- Explore [Merge Strategies](../user-guide/merge-strategies.md) to learn more sophisticated merging
- Check [Advanced Usage](../user-guide/advanced-usage.md) for LLM-powered consolidation
- See [Examples](../examples/examples-overview.md) for real-world scenarios

---

**Need help?** Check out our [FAQ](../faq.md) or open an issue on [GitHub](https://github.com/yifanfeng97/ontomem).
