"""Merger strategies for ontomem."""

from enum import Enum, nonmember
from typing import TypeVar, Callable

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
    CustomRuleMerger,
)

from langchain.chat_models import BaseChatModel


# Type definitions
T = TypeVar("T", bound=BaseModel)


class MergeStrategy(str, Enum):
    """Merge strategy for handling duplicate items.

    This enum defines the standard strategies for merging duplicate items
    when the same unique key is encountered multiple times.

    Strategies:
        KEEP_EXISTING: Keep the existing item, discard the incoming one
        KEEP_INCOMING: Keep the incoming item, discard the existing one (default)
        MERGE_FIELD: Merge fields from both items (new fills old's None fields)

    Example:
        >>> from ontomem.merger import MergeStrategy
        >>> strategy = MergeStrategy.MERGE_FIELD
        >>> print(strategy.value)  # "merge_field"
    """

    KEEP_EXISTING = "keep_existing"
    KEEP_INCOMING = "keep_incoming"
    MERGE_FIELD = "merge_field"

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

        CUSTOM_RULE = "llm_custom_rule"
        """Custom LLM merger with user-defined merge rules."""


def create_merger(
    strategy: str | MergeStrategy,
    key_extractor: callable,
    *,
    llm_client: "BaseChatModel | None" = None,
    item_schema: type[T] | None = None,
    rule: str | None = None,
    dynamic_rule: Callable[[], str] | None = None,
    max_workers: int = 5,
) -> BaseMerger:
    """Factory function to create merger instances.

    Args:
        strategy: MergeStrategy enum value. Can be:
            - Classic strategies: MergeStrategy.KEEP_EXISTING, MergeStrategy.KEEP_INCOMING, MergeStrategy.MERGE_FIELD
            - LLM strategies: MergeStrategy.LLM.BALANCED, MergeStrategy.LLM.PREFER_EXISTING, MergeStrategy.LLM.PREFER_INCOMING
            - Custom LLM: MergeStrategy.LLM.CUSTOM_RULE
        key_extractor: Function to extract unique key from items.
        llm_client: LLM client (required for LLM strategies). Defaults to None.
        item_schema: Pydantic model schema (required for LLM strategies). Defaults to None.
        rule: Static merge rule string (required for CUSTOM_RULE strategy). Defaults to None.
        dynamic_rule: Optional callable returning a string with runtime-specific rules. Defaults to None.
        max_workers: Maximum concurrency for LLM batch calls (LLM strategies only). Defaults to 5.

    Returns:
        Configured BaseMerger instance.

    Raises:
        ValueError: If LLM strategy is used without llm_client or item_schema.
        TypeError: If strategy is not a valid MergeStrategy value.
        ValueError: If CUSTOM_RULE is used without rule parameter.

    Example:
        >>> from ontomem.merger import create_merger, MergeStrategy
        >>> merger = create_merger(
        ...     strategy=MergeStrategy.MERGE_FIELD,
        ...     key_extractor=lambda x: x.id
        ... )
        >>> 
        >>> # Custom rule merger with concurrency control
        >>> merger = create_merger(
        ...     strategy=MergeStrategy.LLM.CUSTOM_RULE,
        ...     key_extractor=lambda x: x.id,
        ...     llm_client=llm,
        ...     item_schema=MySchema,
        ...     rule="Prefer newer emails (incoming). Keep existing names.",
        ...     dynamic_rule=lambda: f"Time context: {datetime.now()}",
        ...     max_workers=3  # Limit to 3 concurrent LLM calls
        ... )
    """
    # Strategy mapper: MergeStrategy value -> Merger class
    strategy_map = {
        MergeStrategy.KEEP_EXISTING: KeepExistingMerger,
        MergeStrategy.KEEP_INCOMING: KeepIncomingMerger,
        MergeStrategy.MERGE_FIELD: FieldMerger,
        MergeStrategy.LLM.BALANCED: BalancedMerger,
        MergeStrategy.LLM.PREFER_EXISTING: PreferExistingMerger,
        MergeStrategy.LLM.PREFER_INCOMING: PreferIncomingMerger,
        MergeStrategy.LLM.CUSTOM_RULE: CustomRuleMerger,
    }

    # Determine if this is an LLM strategy
    is_llm = strategy in (
        MergeStrategy.LLM.BALANCED,
        MergeStrategy.LLM.PREFER_EXISTING,
        MergeStrategy.LLM.PREFER_INCOMING,
        MergeStrategy.LLM.CUSTOM_RULE,
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
        
        # Special handling for CUSTOM_RULE strategy
        if strategy == MergeStrategy.LLM.CUSTOM_RULE:
            if not rule:
                raise ValueError(
                    "Custom Rule LLM strategy requires 'rule' parameter."
                )
            return CustomRuleMerger(
                key_extractor=key_extractor,
                llm_client=llm_client,
                item_schema=item_schema,
                rule=rule,
                dynamic_rule=dynamic_rule,
                max_workers=max_workers,
            )

        merger_cls = strategy_map[strategy]
        return merger_cls(
            key_extractor=key_extractor,
            llm_client=llm_client,
            item_schema=item_schema,
            max_workers=max_workers,
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
    "CustomRuleMerger",
    "MergeStrategy",
    "create_merger",
]
