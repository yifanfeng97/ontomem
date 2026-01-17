"""Balanced LLM merger with no preference."""

from typing import TypeVar

from pydantic import BaseModel

from .base import BaseLLMMerger

T = TypeVar("T", bound=BaseModel)


BALANCED_MERGE_PROMPT = """You are an expert at merging structured data intelligently.

Given two instances of the same item (identified by the same unique key), 
your task is to merge their fields into one complete, accurate item with **NO PREFERENCE** 
between the two versions.

**Merging Rules:**
1. Keep the unique key field unchanged (it's the same in both items)
2. For other fields:
   - If only one item has a non-null value, use that value
   - If both items have values, intelligently choose the more complete/accurate one
   - For list fields, combine unique elements from both
   - For text fields, merge or choose the more informative one
3. Preserve all valuable information from both items
4. Return a single merged item that represents the best combination

**Item A (existing):**
{item_existing}

**Item B (incoming):**
{item_incoming}

**Instructions:**
Analyze both items carefully and return a single merged item that intelligently 
combines information from both sources. Use your judgment to select the best value 
for each field. Ensure the output matches the expected schema."""


class BalancedMerger(BaseLLMMerger[T]):
    """Balanced LLM merger with no preference (default strategy).

    Uses intelligent decision-making to merge conflicting fields
    without favoring either the existing or incoming item.

    Key Features:
        - Batch optimization: Minimizes LLM API calls via tournament algorithm
        - Intelligent conflict resolution: LLM makes semantic decisions
        - Structured output: Returns Pydantic models matching input schema
        - Error handling: Automatic fallback to keep_new strategy

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

    def get_system_prompt(self) -> str:
        """Return the balanced merge system prompt."""
        return BALANCED_MERGE_PROMPT
