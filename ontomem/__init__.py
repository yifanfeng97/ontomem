"""ontomem - Schema-First Stateful Memory Store.

A production-grade Python library for building intelligent semantic memory
with automatic deduplication, merging, and vector-based search.
"""

from .core.omem import OMem
from .core.base import BaseMem
from .merger import (
    BaseMerger,
    FieldMerger,
    KeepNewMerger,
    KeepOldMerger,
    BaseLLMMerger,
    BalancedMerger,
    ExistingFirstMerger,
    IncomingFirstMerger,
    MergeStrategy
)
from .utils.logging import configure_logging, get_logger

__version__ = "0.1.0"

__all__ = [
    # Main API
    "OMem",
    # Core interfaces
    "BaseMem",
    "BaseMerger",
    "BaseLLMMerger",
    # Built-in Strategies
    "KeepNewMerger",
    "KeepOldMerger",
    "FieldMerger",
    "BalancedMerger",
    "ExistingFirstMerger",
    "IncomingFirstMerger",
    # Types
    "MergeStrategy",
    # Utilities
    "configure_logging",
    "get_logger",
]
