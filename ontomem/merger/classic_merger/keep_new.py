"""KeepNewMerger - Always keep the incoming (newer) item."""

from typing import TypeVar

from pydantic import BaseModel

from ..base import BaseMerger

T = TypeVar("T", bound=BaseModel)


class KeepNewMerger(BaseMerger[T]):
    """Merger that always keeps the incoming (newer) item.

    Use case: When you want the most recent version of duplicate items.

    Example:
        >>> merger = KeepNewMerger(key_extractor=lambda x: x.id)
        >>> items = [Item(id=1, version=1), Item(id=1, version=2)]
        >>> merged = merger.merge(items)
        >>> # Result: [Item(id=1, version=2)]
    """

    def pair_merge(self, existing: T, incoming: T) -> T:
        """Keep the incoming item, discard the existing one.

        Args:
            existing: The existing item (will be discarded).
            incoming: The incoming item (will be kept).

        Returns:
            The incoming item.
        """
        return incoming
