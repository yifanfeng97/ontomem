"""Classic deterministic merge strategies."""

from .merge_field import FieldMerger
from .keep_new import KeepNewMerger
from .keep_old import KeepOldMerger

__all__ = [
    "KeepNewMerger",
    "KeepOldMerger",
    "FieldMerger",
]
