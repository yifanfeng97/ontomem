# 01: Self-Improving Debugger

## Overview

An AI debugging agent that learns from each bug it encounters, building an evolving knowledge base of solutions. Each time the same error is encountered, Ontomem consolidates previous experiences using LLM-powered merging to generate better solutions.

## Theme

**Error Learning & Consolidation**

## Strategy

**LLM.BALANCED merge** with intelligent consolidation

## Key Features

- ✅ Multiple error encounters of the same type
- ✅ LLM-based intelligent merging of solutions
- ✅ Cross-encounter learning and synthesis
- ✅ Memory persistence for future debugging sessions
- ✅ Progressive refinement of debugging wisdom

## Data Structure

### DebugLog
```python
error_id: str                      # Unique error identifier
error_type: str                    # Type of error
error_message: str                 # Error message
stack_trace: str | None            # Stack trace
solutions: list[str]               # Multiple solutions found
attempted_fixes: list[str]         # Fixes tried so far
root_cause: str | None             # Inferred root cause
```

## Use Case

**AI Development & Debugging**: A debugging assistant that learns from each error, automatically consolidates solutions, and synthesizes debugging wisdom to help developers solve problems faster.

**Benefits**:
- Automatic knowledge accumulation
- Cross-project error pattern recognition
- Synthesized best practices over time
- Reduced time to resolution

## Running the Example

```bash
cd examples/
python 01_self_improving_debugger.py
```

## Output

Results are stored in `temp/debugger_memory/`:
- `memory.json`: Consolidated error records with merged solutions
- `metadata.json`: Schema and statistics

## What You'll Learn

1. **Error Consolidation**: How to merge information from multiple error encounters
2. **LLM-Powered Merging**: Using LLM to intelligently synthesize conflicting solutions
3. **Cross-Encounter Learning**: Building wisdom from multiple similar problems
4. **Memory Persistence**: Saving and retrieving consolidated knowledge

## Related Concepts

- [Merge Strategies](../user-guide/merge-strategies.md)
- [LLM Integration](../user-guide/llm-integration.md)
- [Persistence](../user-guide/persistence.md)

## Next Examples

- [02: RPG NPC Memory](02-rpg-npc-memory.md) - Field-based profile building
- [04: Multi-Source Fusion](04-multi-source-fusion.md) - Advanced conflict resolution
