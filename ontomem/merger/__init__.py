"""Merger strategies for ontomem."""

from enum import Enum, nonmember
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

from .base import BaseMerger
from .classic_merger.merge_field import FieldMerger
from .classic_merger.keep_incoming import KeepIncomingMerger
from .classic_merger.keep_existing import KeepExistingMerger
from .llm_merger import (
    BaseLLMMerger,
    BalancedMerger,
    PreferExistingMerger,
    PreferIncomingMerger,
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
        KEEP_EXISTING: Keep the existing item, discard the incoming one
        KEEP_INCOMING: Keep the incoming item, discard the existing one (default)
        FIELD_MERGE: Merge fields from both items (new fills old's None fields)

    Example:
        >>> from ontomem.merger import MergeStrategy
        >>> strategy = MergeStrategy.FIELD_MERGE
        >>> print(strategy.value)  # "field_merge"
    """

    KEEP_OLD = "keep_old"  # Backwards compatible alias for KEEP_EXISTING
    KEEP_NEW = "keep_new"  # Backwards compatible alias for KEEP_INCOMING
    FIELD_MERGE = "field_merge"

    @nonmember
    class LLM:
        """LLM-powered merge strategies namespace.

        These strategies use Language Models to intelligently merge items,
        with different semantic conflict resolution preferences.

        Usage:
            >>> from ontomem.merger import MergeStrategy
            >>> strategy = MergeStrategy.LLM.BALANCED  # "llm_balanced"
        """

        BALANCED = "llm_balanced"
        """Balanced merging with no preference between existing and incoming."""

        PREFER_EXISTING = "llm_prefer_existing"
        """When semantic conflicts arise, prioritize existing item values."""

        PREFER_INCOMING = "llm_prefer_incoming"
        """When semantic conflicts arise, prioritize incoming item values."""


def create_merger(
    strategy: str | MergeStrategy,
    key_extractor: callable,
    llm_client: "ChatOpenAI | None" = None,
    item_schema: type[T] | None = None,
) -> BaseMerger:
    """Factory function to create merger instances.

    Args:
        strategy: MergeStrategy enum value. Can be:
            - Classic strategies: MergeStrategy.KEEP_EXISTING, MergeStrategy.KEEP_INCOMING, MergeStrategy.FIELD_MERGE
            - LLM strategies: MergeStrategy.LLM.BALANCED, MergeStrategy.LLM.PREFER_EXISTING, MergeStrategy.LLM.PREFER_INCOMING
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
        MergeStrategy.KEEP_OLD: KeepExistingMerger,
        MergeStrategy.KEEP_NEW: KeepIncomingMerger,
        MergeStrategy.FIELD_MERGE: FieldMerger,
        MergeStrategy.LLM.BALANCED: BalancedMerger,
        MergeStrategy.LLM.PREFER_EXISTING: PreferExistingMerger,
        MergeStrategy.LLM.PREFER_INCOMING: PreferIncomingMerger,
    }

    # Determine if this is an LLM strategy
    is_llm = strategy in (
        MergeStrategy.LLM.BALANCED,
        MergeStrategy.LLM.PREFER_EXISTING,
        MergeStrategy.LLM.PREFER_INCOMING,
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
    "KeepIncomingMerger",
    "KeepExistingMerger",
    "BaseLLMMerger",
    "BalancedMerger",
    "PreferExistingMerger",
    "PreferIncomingMerger",
    "MergeStrategy",
    "create_merger",
]
