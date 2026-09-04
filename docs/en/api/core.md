# Overview

OntoMem provides a comprehensive, well-structured API for building intelligent memory systems. This section covers the core modules and classes.

## Core Modules

### `ontomem.core`
The main module containing the OMem class and base classes.

- **OMem**: Main memory management class
  - Core: `add` / `remove` / `remove_many` / `get` / `upsert` / `clear`
  - Index: `build_index` / `sync_index` (in-place patch) / `clear_index` / `index_built`
  - Editing: `edit(key, remove_fact=|instruction=, dry_run=)` — LLM-assisted semantic editing
  - Search: `search(query, top_k)`
  - Provenance (v0.4.0, `track_sources=True`): `add(items, source_id=)` / `remove_source` / `upsert_source` / `sources` / `dump_sources` / `load_sources` / `suspended_index`
- **BaseMem**: Abstract base class for memory implementations

### `ontomem.merger`
Merge strategy implementations for conflict resolution.

- **Classic Strategies**: Field-based merging, keep incoming, keep existing
- **LLM Strategies**: Intelligent synthesis, preference-based merging

### `ontomem.utils`
Utility functions and helpers.

- **Logging**: Structured logging utilities
- **Type helpers**: Common type definitions

---

## Detailed Module Documentation

For detailed information about specific modules:

- [Core Module](core.md)
- [Merger Module](merger.md)
- [Utils Module](utils.md)

---

See the [Quick Start](../../quick-start.md) to get started immediately.
