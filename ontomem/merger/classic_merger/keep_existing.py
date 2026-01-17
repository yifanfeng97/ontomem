"""KeepExistingMerger - Always keep the existing (older) item."""

from typing import TypeVar

from pydantic import BaseModel

from ..base import BaseMerger

T = TypeVar("T", bound=BaseModel)


class KeepExistingMerger(BaseMerger[T]):
    """Merger that always keeps the existing (older) item.

    Use case: When you want to preserve the first occurrence of duplicate items.

    Example:
        >>> merger = KeepExistingMerger(key_extractor=lambda x: x.id)
        >>> items = [Item(id=1, version=1), Item(id=1, version=2)]
        >>> merged = merger.merge(items)
        >>> # Result: [Item(id=1, version=1)]
    """

    def pair_merge(self, existing: T, incoming: T) -> T:
        """Keep the existing item, discard the incoming one.

        Args:
            existing: The existing item (will be kept).
            incoming: The incoming item (will be discarded).

        Returns:
            The existing item.
        """
        return existing
