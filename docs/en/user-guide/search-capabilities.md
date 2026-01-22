# Search Capabilities

Learn how to search your memory effectively.

## Key-Based Lookup

Fast, exact matching using unique keys:

```python
researcher = memory.get("Yann LeCun")
if researcher:
    print(f"Found: {researcher.name}")
```

**Performance**: O(1) - Constant time, blazingly fast.

---

## Semantic Search

Find entities by meaning, not exact keys:

```python
memory.build_index()
results = memory.search("deep learning research papers", top_k=5)

for result in results:
    print(result.name, result.research_focus)
```

**Performance**: O(n) similarity computation + FAISS optimization.

### Building the Index

```python
# Build from scratch
memory.build_index()

# Force rebuild (useful after many updates)
memory.build_index(force=True)
```

### Search Parameters

```python
results = memory.search(
    query="artificial intelligence",  # Natural language query
    top_k=10                              # Return top 10 results
)
```

- **query**: Natural language string describing what you're looking for
- **top_k**: Number of top results to return (default: 5)

---

## Combining Search Methods

```python
# First, narrow with semantic search
candidates = memory.search("machine learning", top_k=20)

# Then, verify with exact lookup
specific = memory.get("Yann LeCun")

# Filter results
active_researchers = [r for r in candidates if r.is_active]
```

---

## Search Best Practices

1. **Use semantic search for discovery** - Find conceptually related items
2. **Use key lookup for known items** - Direct access is faster
3. **Refine query terms** - Better queries = better results
4. **Adjust k based on needs** - Start with k=5, increase if needed

See more in [Advanced Usage](advanced-usage.md).
