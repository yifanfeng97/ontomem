"""Merger strategies for ontomem."""

from enum import Enum, nonmember
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

from .base import BaseMerger
from .classic_merger.merge_field import FieldMerger
from .classic_merger.keep_new import KeepNewMerger
from .classic_merger.keep_old import KeepOldMerger
from .llm_merger import (
    BaseLLMMerger,
    BalancedMerger,
    ExistingFirstMerger,
    IncomingFirstMerger,
)

if TYPE_CHECKING:
    from langchain.chat_models import ChatOpenAI

# Type definitions
T = TypeVar("T", bound=BaseModel)


class MergeStrategy(str, Enum):
    """Merge strategy for handling duplicate items.

    This enum defines the standard strategies for merging duplicate items
    when the same unique key is encountered multiple times.

    Strategies:
        KEEP_OLD: Keep the existing item, discard the new one
        KEEP_NEW: Keep the new item, discard the existing one (default)
        FIELD_MERGE: Merge fields from both items (new fills old's None fields)

    Example:
        >>> from ontomem.merger import MergeStrategy
        >>> strategy = MergeStrategy.FIELD_MERGE
        >>> print(strategy.value)  # "field_merge"
    """

    KEEP_OLD = "keep_old"
    KEEP_NEW = "keep_new"
    FIELD_MERGE = "field_merge"

    @nonmember
    class LLM:
        """LLM-powered merge strategies namespace.

        These strategies use Language Models to intelligently merge items,
        with different conflict resolution preferences.

        Usage:
            >>> from ontomem.merger import MergeStrategy
            >>> strategy = MergeStrategy.LLM.BALANCED  # "llm_balanced"
        """

        BALANCED = "llm_balanced"
        """Balanced merging with no preference between existing and incoming."""

        EXISTING_FIRST = "llm_existing_first"
        """Prioritize existing item values, use incoming only for gaps."""

        INCOMING_FIRST = "llm_incoming_first"
        """Prioritize incoming item values, use existing only for gaps."""


def create_merger(
    strategy: str | MergeStrategy,
    key_extractor: callable,
    llm_client: "ChatOpenAI | None" = None,
    item_schema: type[T] | None = None,
) -> BaseMerger:
    """Factory function to create merger instances.

    Args:
        strategy: MergeStrategy enum value. Can be:
            - Classic strategies: MergeStrategy.KEEP_OLD, MergeStrategy.KEEP_NEW, MergeStrategy.FIELD_MERGE
            - LLM strategies: MergeStrategy.LLM.BALANCED, MergeStrategy.LLM.EXISTING_FIRST, MergeStrategy.LLM.INCOMING_FIRST
        key_extractor: Function to extract unique key from items.
        llm_client: LLM client (required for LLM strategies). Defaults to None.
        item_schema: Pydantic model schema (required for LLM strategies). Defaults to None.

    Returns:
        Configured BaseMerger instance.

    Raises:
        ValueError: If LLM strategy is used without llm_client or item_schema.
        TypeError: If strategy is not a valid MergeStrategy value.

    Example:
        >>> from ontomem.merger import create_merger, MergeStrategy
        >>> merger = create_merger(
        ...     strategy=MergeStrategy.FIELD_MERGE,
        ...     key_extractor=lambda x: x.id
        ... )
    """
    # Strategy mapper: MergeStrategy value -> Merger class
    strategy_map = {
        MergeStrategy.KEEP_OLD: KeepOldMerger,
        MergeStrategy.KEEP_NEW: KeepNewMerger,
        MergeStrategy.FIELD_MERGE: FieldMerger,
        MergeStrategy.LLM.BALANCED: BalancedMerger,
        MergeStrategy.LLM.EXISTING_FIRST: ExistingFirstMerger,
        MergeStrategy.LLM.INCOMING_FIRST: IncomingFirstMerger,
    }

    # Determine if this is an LLM strategy
    is_llm = strategy in (
        MergeStrategy.LLM.BALANCED,
        MergeStrategy.LLM.EXISTING_FIRST,
        MergeStrategy.LLM.INCOMING_FIRST,
    )

    # Validate strategy
    if strategy not in strategy_map:
        raise TypeError(
            f"Unknown strategy '{strategy}'. "
            f"Use MergeStrategy enum values: {list(strategy_map.keys())}"
        )

    # LLM strategies require additional parameters
    if is_llm:
        if not llm_client:
            raise ValueError(
                f"LLM strategy '{strategy}' requires llm_client parameter."
            )
        if not item_schema:
            raise ValueError(
                f"LLM strategy '{strategy}' requires item_schema parameter."
            )
        merger_cls = strategy_map[strategy]
        return merger_cls(
            key_extractor=key_extractor,
            llm_client=llm_client,
            item_schema=item_schema,
        )

    # Classic strategies
    merger_cls = strategy_map[strategy]
    return merger_cls(key_extractor)


__all__ = [
    "BaseMerger",
    "FieldMerger",
    "KeepNewMerger",
    "KeepOldMerger",
    "BaseLLMMerger",
    "BalancedMerger",
    "ExistingFirstMerger",
    "IncomingFirstMerger",
    "MergeStrategy",
    "create_merger",
]
