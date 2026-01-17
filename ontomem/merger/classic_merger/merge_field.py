"""FieldMerger - Merge at field level for Pydantic models."""

from typing import TypeVar

from pydantic import BaseModel

from ...utils.logging import get_logger
from ..base import BaseMerger

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class FieldMerger(BaseMerger[T]):
    """Merger that combines fields from both items (Pydantic models).

    Merge strategy:
        1. Start with existing item as base (get all non-None fields)
        2. Overlay incoming item's non-None fields on top
        3. Result: Most complete item with new data taking precedence

    Requirements:
        - Items must be Pydantic BaseModel instances
        - Items must have compatible schemas

    Use case: Accumulating information across multiple extractions.

    Example:
        >>> from pydantic import BaseModel
        >>> class Person(BaseModel):
        ...     name: str
        ...     age: int | None = None
        ...     city: str | None = None
        >>>
        >>> merger = FieldMerger(key_extractor=lambda x: x.name)
        >>> items = [
        ...     Person(name="Alice", age=30, city=None),
        ...     Person(name="Alice", age=None, city="NYC"),
        ... ]
        >>> merged = merger.merge(items)
        >>> # Result: [Person(name="Alice", age=30, city="NYC")]
    """

    def pair_merge(self, existing: T, incoming: T) -> T:
        """Merge fields from both items, with incoming taking precedence.

        Strategy:
            - Start with existing item's non-None values as base
            - Overlay incoming item's non-None values on top
            - Result: Existing fields + new fields from incoming

        Args:
            existing: The existing item.
            incoming: The incoming item.

        Returns:
            Merged item with fields from both.

        Raises:
            AttributeError: If items are not Pydantic models.
        """
        try:
            # Get all non-None fields from existing as base
            merged_data = existing.model_dump(exclude_none=True)
            # Overlay incoming's non-None values (new data takes precedence)
            merged_data.update(incoming.model_dump(exclude_none=True))
            # Reconstruct item with merged data
            return type(incoming)(**merged_data)
        except AttributeError as e:
            logger.error(
                f"FieldMerger requires Pydantic BaseModel instances. "
                f"Got types: {type(existing)}, {type(incoming)}. Error: {e}"
            )
            # Fallback to keep incoming
            return incoming
        except Exception as e:
            logger.error(
                f"FieldMerger failed during merge: {e}. "
                f"Falling back to keep incoming."
            )
            return incoming
