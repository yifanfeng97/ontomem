"""Base class for LLM-powered merge strategies."""

from abc import abstractmethod
from typing import Any, Callable, List, Tuple, TypeVar

from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from ..base import BaseMerger
from ...utils.logging import get_logger

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class BaseLLMMerger(BaseMerger[T]):
    """Abstract base class for LLM-powered merge strategies.

    This class extends BaseMerger to provide unified LLM merging functionality.
    All concrete strategies inherit this implementation and only need to define
    their system prompt via get_system_prompt().

    Subclasses should override:
    - get_system_prompt(): Return the system prompt string for merge behavior
    - optionally override pair_merge() for custom fallback behavior
    """

    def __init__(
        self,
        key_extractor: Callable[[T], Any],
        llm_client: BaseChatModel,
        item_schema: type[T],
    ):
        """Initialize LLM merger.

        Args:
            key_extractor: Function to extract unique key from an item.
            llm_client: LangChain LLM instance (e.g., ChatOpenAI).
            item_schema: Pydantic model class of items.
        """
        super().__init__(key_extractor)
        self.llm_client = llm_client
        self.item_schema = item_schema
        self.logger = logger

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this merge strategy.

        Subclasses override this to define their merge behavior.

        Returns:
            System prompt string.
        """
        pass

    def _create_merge_chain(self):
        """Create the LLM merge chain with structured output."""
        system_prompt = self.get_system_prompt()

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Item A (existing):\n{item_existing}\n\nItem B (incoming):\n{item_incoming}")
        ])

        return prompt_template | self.llm_client.with_structured_output(self.item_schema)

    def pair_merge(self, existing: T, incoming: T) -> T:
        """Merge a single pair using LLM (default implementation).

        This method is used as a fallback when batch_merge fails or when
        called directly. For best performance, batch_merge() should be used.

        Args:
            existing: The existing item.
            incoming: The incoming item.

        Returns:
            Merged item from LLM, or incoming item if LLM fails.
        """
        try:
            self.logger.debug("Performing single LLM merge (fallback)")
            merge_chain = self._create_merge_chain()
            merged = merge_chain.invoke({
                "item_existing": existing.model_dump_json(indent=2),
                "item_incoming": incoming.model_dump_json(indent=2),
            })
            return merged
        except Exception as e:
            self.logger.error(
                f"LLM pair merge failed: {e}. Falling back to keep_new strategy."
            )
            return incoming

    def batch_merge(self, pairs: List[Tuple[T, T]]) -> List[T]:
        """Batch merge multiple pairs using LLM (optimized).

        This unified implementation is used by all LLM-based strategies.
        The behavior is controlled by get_system_prompt() from subclasses.

        Args:
            pairs: List of (existing, incoming) tuples to merge.

        Returns:
            List of merged items (same order as input).
        """
        if not pairs:
            return []

        merge_chain = self._create_merge_chain()

        self.logger.info(
            f"Batch merging {len(pairs)} pairs with LLM "
            f"(single API call instead of {len(pairs)} calls)"
        )

        # Prepare batch inputs
        inputs = [
            {
                "item_existing": existing.model_dump_json(indent=2),
                "item_incoming": incoming.model_dump_json(indent=2),
            }
            for existing, incoming in pairs
        ]

        try:
            # Critical: Single batch API call for all pairs
            merged_results = merge_chain.batch(inputs)
            self.logger.info(f"Successfully batch merged {len(merged_results)} pairs")
            return merged_results

        except Exception as e:
            self.logger.error(
                f"Batch LLM merge failed: {e}. "
                f"Falling back to sequential pair_merge for {len(pairs)} pairs."
            )

            # Fallback: Sequential pair merges
            results = []
            for existing, incoming in pairs:
                merged = self.pair_merge(existing, incoming)
                results.append(merged)

            return results
