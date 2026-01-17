"""Base merger class with tournament-style merge algorithm.

The tournament merge algorithm efficiently handles n-way merging of duplicate items
by organizing merges into logarithmic rounds, similar to tournament elimination.
"""

import logging
import math
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar

from pydantic import BaseModel

from ..utils.logging import get_logger

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class BaseMerger(ABC, Generic[T]):
    """Abstract base class for item mergers with tournament-style merge algorithm.

    This class provides the core tournament merge algorithm that efficiently handles
    n duplicate items by organizing merges into O(log n) rounds. Each round collects
    all merge tasks across ALL unique keys and processes them in a single batch,
    maximizing efficiency for batch operations (e.g., LLM API calls).

    Key Features:
        - Tournament algorithm: O(log n) rounds for n duplicate items
        - Batch optimization: Each round processes ALL keys' pairs together
        - Automatic deduplication: Based on key_extractor function
        - Pluggable strategies: Subclasses implement pair_merge() and optionally batch_merge()

    Subclass Requirements:
        - Must implement: pair_merge(existing, incoming) -> merged_item
        - Optional override: batch_merge(pairs) -> merged_items (for batch optimization)

    Algorithm Example (5 duplicate items for one key):
        Initial: [i1, i2, i3, i4, i5]

        Round 1: Pair up [(i1,i2), (i3,i4)], advance [i5]
            → batch_merge([(i1,i2), (i3,i4)]) → [m12, m34]
            → Next round: [m12, m34, i5]

        Round 2: Pair up [(m12,m34)], advance [i5]
            → batch_merge([(m12,m34)]) → [m1234]
            → Next round: [m1234, i5]

        Round 3: Pair up [(m1234,i5)]
            → batch_merge([(m1234,i5)]) → [final]

        Total: 3 rounds, 4 merge operations (all batchable)

    Example:
        >>> class SimpleKeepNewMerger(BaseMerger[Item]):
        ...     def pair_merge(self, existing, incoming):
        ...         return incoming
        >>>
        >>> merger = SimpleKeepNewMerger(key_extractor=lambda x: x.id)
        >>> merged_items = merger.merge(items)
    """

    def __init__(
        self,
        key_extractor: Callable[[T], Any],
        *,
        logger_instance: Optional[logging.Logger] = None,
    ):
        """Initialize the merger.

        Args:
            key_extractor: Function to extract unique key from an item.
                          Example: lambda x: x.id or lambda x: x.name
            logger_instance: Optional logger instance for progress tracking.
                           If None, uses module-level logger.
        """
        self.key_extractor = key_extractor
        self.logger = logger_instance or logger

    # ==================== Abstract Methods ====================

    @abstractmethod
    def pair_merge(self, existing: T, incoming: T) -> T:
        """Merge two items (must be implemented by subclasses).

        This method defines how to merge a pair of duplicate items.

        Args:
            existing: The existing item.
            incoming: The incoming item to merge with existing.

        Returns:
            The merged item.

        Example:
            >>> def pair_merge(self, existing, incoming):
            ...     # Keep the newer item
            ...     return incoming
        """
        pass

    def batch_merge(self, pairs: List[tuple[T, T]]) -> List[T]:
        """Batch merge multiple pairs (optional override for optimization).

        Default implementation: Sequentially call pair_merge() for each pair.

        Subclasses should override this method to implement true batch optimization,
        such as batching LLM API calls to reduce latency and cost.

        Args:
            pairs: List of (existing, incoming) tuples to merge.

        Returns:
            List of merged items (same order as input pairs).

        Example (LLM optimization):
            >>> def batch_merge(self, pairs):
            ...     # Prepare batch inputs
            ...     inputs = [{"a": a.json(), "b": b.json()} for a, b in pairs]
            ...     # Single batch API call
            ...     return llm_chain.batch(inputs)
        """
        results = []
        for existing, incoming in pairs:
            merged = self.pair_merge(existing, incoming)
            results.append(merged)
        return results

    # ==================== Core Algorithm ====================

    def merge(self, items: List[T]) -> List[T]:
        """Main entry point: Deduplicate and merge items with cross-key batching.

        Algorithm:
            1. Group items by unique key
            2. Run tournament merge across ALL keys simultaneously
            3. Each round collects pairs from ALL keys → single batch_merge() call
            4. Return list of merged items

        This cross-key batching significantly improves efficiency for batch operations
        (e.g., LLM API calls), reducing total API calls by orders of magnitude.

        Args:
            items: List of items to merge (may contain duplicates).

        Returns:
            List of deduplicated and merged items.

        Example:
            >>> items = [
            ...     Item(id=1, name="Alice", age=None),
            ...     Item(id=1, name=None, age=30),
            ...     Item(id=2, name="Bob", age=25),
            ...     Item(id=2, name="Bob", city="NYC"),
            ... ]
            >>> merger = FieldMerger(key_extractor=lambda x: x.id)
            >>> merged = merger.merge(items)
            >>> # Round 1: Batch merge [(Alice1, Alice2), (Bob1, Bob2)] in ONE call
            >>> # Result: [Item(id=1, name="Alice", age=30), Item(id=2, name="Bob", city="NYC")]
        """
        if not items:
            return []

        # Step 1: Group items by unique key
        groups = self._group_by_key(items)

        self.logger.info(f"Grouped {len(items)} items into {len(groups)} unique keys")

        # Step 2: Cross-key tournament merge
        merged_items = self._cross_key_tournament_merge(groups)

        self.logger.info(f"Merged into {len(merged_items)} unique items")

        return merged_items

    def _group_by_key(self, items: List[T]) -> dict[Any, List[T]]:
        """Group items by their unique key.

        Args:
            items: List of items to group.

        Returns:
            Dictionary mapping key -> list of items with that key.

        Example:
            >>> items = [Item(id=1, ...), Item(id=1, ...), Item(id=2, ...)]
            >>> groups = self._group_by_key(items)
            >>> # Result: {1: [Item(id=1, ...), Item(id=1, ...)], 2: [Item(id=2, ...)]}
        """
        from collections import defaultdict

        groups = defaultdict(list)
        for item in items:
            try:
                key = self.key_extractor(item)
                if key is not None:
                    groups[key].append(item)
                else:
                    self.logger.warning(f"Item has None key, skipping: {item}")
            except Exception as e:
                self.logger.warning(f"Failed to extract key from item: {e}")
        return dict(groups)

    def _cross_key_tournament_merge(self, groups: Dict[Any, List[T]]) -> List[T]:
        """Cross-key tournament merge: Process all keys simultaneously.

        **Key Optimization**: Instead of merging each key independently, this method
        runs tournament rounds across ALL keys, collecting all pairs from all keys
        in each round and processing them in a single batch_merge() call.

        Performance Impact:
            - Old approach: K keys × log(M) rounds × 1 batch call = K×log(M) API calls
            - New approach: log(max_M) rounds × 1 batch call = log(max_M) API calls
            - Speedup: K× reduction in API calls

        Algorithm:
            1. Initialize each key with its list of items
            2. Round 1: For each key, pair up items → collect ALL pairs → batch merge
            3. Round 2: For each key, pair up results → collect ALL pairs → batch merge
            4. Continue until each key has only 1 item

        Args:
            groups: Dictionary mapping key -> list of items with that key.

        Returns:
            List of merged items (one per unique key).

        Example (2 keys, 4 items each):
            Initial:
                key1: [i1a, i1b, i1c, i1d]
                key2: [i2a, i2b, i2c, i2d]

            Round 1: Collect ALL pairs from ALL keys
                key1 pairs: [(i1a,i1b), (i1c,i1d)]
                key2 pairs: [(i2a,i2b), (i2c,i2d)]
                ALL pairs: [(i1a,i1b), (i1c,i1d), (i2a,i2b), (i2c,i2d)]
                batch_merge(ALL 4 pairs) → [m1ab, m1cd, m2ab, m2cd]
                Next round:
                    key1: [m1ab, m1cd]
                    key2: [m2ab, m2cd]

            Round 2: Collect ALL pairs from ALL keys
                key1 pairs: [(m1ab,m1cd)]
                key2 pairs: [(m2ab,m2cd)]
                ALL pairs: [(m1ab,m1cd), (m2ab,m2cd)]
                batch_merge(ALL 2 pairs) → [final1, final2]

            Result: [final1, final2]
            Total API calls: 2 (vs 4 in old approach)
        """
        # Track current round of items for each key
        key_rounds: Dict[Any, List[T]] = {
            key: items[:] for key, items in groups.items()
        }

        round_num = 0
        max_rounds = max(
            math.ceil(math.log2(len(items))) if len(items) > 1 else 0
            for items in groups.values()
        )

        self.logger.debug(
            f"Starting cross-key tournament merge for {len(groups)} keys "
            f"(max {max_rounds} rounds)"
        )

        # Continue until all keys have exactly 1 item
        while any(len(items) > 1 for items in key_rounds.values()):
            round_num += 1
            all_pairs: List[Tuple[T, T]] = []  # Collect pairs from ALL keys
            pair_to_key = []  # Track which key each pair belongs to

            # For each key, pair up items in current round
            for key, current_items in key_rounds.items():
                if len(current_items) <= 1:
                    continue  # This key is done

                # Pair up: (0,1), (2,3), (4,5), ...
                for i in range(0, len(current_items) - 1, 2):
                    all_pairs.append((current_items[i], current_items[i + 1]))
                    pair_to_key.append(key)

            # Batch merge ALL pairs from ALL keys in ONE call
            if all_pairs:
                self.logger.debug(
                    f"Round {round_num}/{max_rounds}: Batch merging {len(all_pairs)} pairs "
                    f"from {len([k for k, items in key_rounds.items() if len(items) > 1])} keys"
                )

                merged_results = self.batch_merge(all_pairs)

                # Distribute results back to keys
                result_idx = 0
                for key in key_rounds.keys():
                    if len(key_rounds[key]) <= 1:
                        continue

                    next_round = []

                    # Add merged results for this key's pairs
                    key_pair_count = sum(1 for k in pair_to_key if k == key)
                    for _ in range(key_pair_count):
                        next_round.append(merged_results[result_idx])
                        result_idx += 1

                    # Add odd item if exists
                    if len(key_rounds[key]) % 2 == 1:
                        next_round.append(key_rounds[key][-1])

                    key_rounds[key] = next_round

        # Extract final merged item for each key
        merged_items = [items[0] for items in key_rounds.values()]

        self.logger.debug(f"Cross-key tournament merge completed in {round_num} rounds")

        return merged_items
