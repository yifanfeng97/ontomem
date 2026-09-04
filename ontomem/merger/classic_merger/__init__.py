"""Classic deterministic merge strategies."""

from .keep_existing import KeepExistingMerger
from .keep_incoming import KeepIncomingMerger
from .merge_field import FieldMerger

__all__ = [
    "FieldMerger",
    "KeepExistingMerger",
    "KeepIncomingMerger",
]
