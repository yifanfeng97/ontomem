# 03: Semantic Scholar

## Overview

Builds a searchable research paper library with semantic search capabilities. Papers can be discovered by content similarity through vector embeddings, not just keywords. Demonstrates the power of hybrid search combining exact lookup with semantic similarity.

## Theme

**Academic Paper Library**

## Strategy

**Vector search + persistence**

## Key Features

- ✅ Vector embeddings for semantic search (requires OpenAI API)
- ✅ Metadata management (citations, keywords, relationships)
- ✅ Library statistics and analysis
- ✅ Persistence of indexed papers
- ✅ Fast retrieval and discovery

## Data Structure

### ResearchPaper
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

## Use Case

**Academic & Research Systems**: Build searchable research databases where papers can be discovered by semantic similarity. Researchers can find related work not just by keywords but by conceptual similarity.

**Benefits**:
- Discovery of related research beyond keyword matching
- Automatic paper recommendation
- Research trend tracking
- Literature review acceleration

## Running the Example

```bash
cd examples/

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

python 03_semantic_scholar.py
```

## Output

Results are stored in `temp/scholar_library/`:
- `memory.json`: Paper records with metadata
- `metadata.json`: Schema and statistics
- `faiss_index/`: Vector index for semantic search

## API Requirements ✅ Required

This example requires an **OpenAI API key** for generating embeddings.

## What You'll Learn

1. **Vector Embeddings**: How to use embeddings for semantic search
2. **Hybrid Search**: Combining key-value lookup with semantic similarity
3. **FAISS Indexing**: Persistent vector index management
4. **Similarity Search**: Finding related items by semantic meaning

## Related Concepts

- [Semantic Search](../user-guide/search-capabilities.md)
- [Vector Indexing](../user-guide/vector-indexing.md)
- [Persistence](../user-guide/persistence.md)

## Next Examples

- [04: Multi-Source Fusion](04-multi-source-fusion.md) - Advanced data integration
- [06: Temporal Memory](06-temporal-memory-consolidation.md) - Time-series patterns
