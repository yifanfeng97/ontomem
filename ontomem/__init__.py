"""ontomem - Schema-First Stateful Memory Store.

A production-grade Python library for building intelligent semantic memory
with automatic deduplication, merging, and vector-based search.
"""

from .core.omem import OMem
from .core.base import BaseMem
from .merger import (
    MergeStrategy,
    BaseMerger,
    FieldMerger,
    KeepIncomingMerger,
    KeepExistingMerger,
    BaseLLMMerger,
    BalancedMerger,
    PreferExistingMerger,
    PreferIncomingMerger
)
from .utils.logging import configure_logging, get_logger

__version__ = "0.1.8"
__author__ = "Yifan Feng"
__email__ = "evanfeng97@gmail.com"

__all__ = [
    # Main API
    "OMem",
    # Core interfaces
    "BaseMem",
    "BaseMerger",
    "BaseLLMMerger",
    # Built-in Strategies
    "KeepIncomingMerger",
    "KeepExistingMerger",
    "FieldMerger",
    "BalancedMerger",
    "PreferExistingMerger",
    "PreferIncomingMerger",
    # Types
    "MergeStrategy",
    # Utilities
    "configure_logging",
    "get_logger",
]
