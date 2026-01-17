"""Classic deterministic merge strategies."""

from .merge_field import FieldMerger
from .keep_existing import KeepExistingMerger
from .keep_incoming import KeepIncomingMerger

__all__ = [
    "KeepIncomingMerger",
    "KeepExistingMerger",
    "FieldMerger",
]
