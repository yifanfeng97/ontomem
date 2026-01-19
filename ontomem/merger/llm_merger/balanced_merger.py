"""Balanced LLM merger with no preference."""

from typing import TypeVar

from pydantic import BaseModel

from .base import BaseLLMMerger

T = TypeVar("T", bound=BaseModel)


BALANCED_MERGE_PROMPT = """You are an intelligent data merging assistant.
You will merge two JSON objects representing the same entity: Item A (existing) and Item B (incoming).

Merge strategy:
1. Combine information from both items.
2. If fields conflict, use your best judgment to pick the more detailed or recent-looking value.
3. If one item has a null/missing value and the other has data, keep the data.
4. For list fields, combine unique elements from both.
5. Do not invent new information not present in the inputs.
6. Return the result in the exact JSON format of the input items."""


class BalancedMerger(BaseLLMMerger[T]):
    """Balanced LLM merger with no preference (default strategy).

    Uses intelligent decision-making to merge conflicting fields
    without favoring either the existing or incoming item.

    Key Features:
        - Batch optimization: Minimizes LLM API calls via tournament algorithm
        - Intelligent conflict resolution: LLM makes semantic decisions
        - Structured output: Returns Pydantic models matching input schema
        - Error handling: Automatic fallback to keep_incoming strategy

    Performance:
        - Without batching: N duplicate items = N API calls
        - With batching: N duplicate items = O(log N) API calls
        - Typical speedup: 10-100x reduction in API calls

    Use case: When you want the LLM to make optimal semantic decisions
    without favoring either the existing or incoming data.

    Example:
        >>> from pydantic import BaseModel
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> class User(BaseModel):
        ...     uid: str
        ...     name: str | None = None
        ...     email: str | None = None
        >>>
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> merger = BalancedMerger(
        ...     key_extractor=lambda x: x.uid,
        ...     llm_client=llm,
        ...     item_schema=User,
        ... )
        >>>
        >>> items = [
        ...     User(uid="u1", name="Alice", email=None),
        ...     User(uid="u1", name=None, email="alice@example.com"),
        ... ]
        >>>
        >>> merged = merger.merge(items)
        >>> # Result: User(uid="u1", name="Alice", email="alice@example.com")
    """

    @property
    def system_prompt(self) -> str:
        """Return the balanced merge system prompt."""
        return BALANCED_MERGE_PROMPT
