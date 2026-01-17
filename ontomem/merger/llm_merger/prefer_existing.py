"""LLM merger that prefers existing item values on semantic conflicts."""

from typing import TypeVar

from pydantic import BaseModel

from .base import BaseLLMMerger

T = TypeVar("T", bound=BaseModel)


EXISTING_PROMPT = """You are an expert at merging structured data intelligently.

Given two instances of the same item (identified by the same unique key), 
merge them into one complete item by combining information from both.

**Merging Rules:**
1. Keep the unique key field unchanged
2. For other fields:
   - If one has a None/empty value and the other has data, use the data
   - If both have values but they conflict semantically (both are valid but different), 
     prefer the **existing item's value**
   - For list fields, combine both lists and remove duplicates
3. Goal: Create the most complete merged item

**Item A (existing):**
{item_existing}

**Item B (incoming):**
{item_incoming}

**Instructions:**
Merge the items intelligently. When semantic conflicts arise, choose the existing value.
Ensure the output matches the expected schema."""


class PreferExistingMerger(BaseLLMMerger[T]):
    """LLM merger that prefers existing item values when semantic conflicts arise.

    Merges information from both items, combining data to create a complete result.
    When semantic conflicts occur (both items have valid but different values), 
    the existing item's value is preferred.

    Key Features:
        - Batch optimization: Minimizes LLM API calls via tournament algorithm
        - Preservation strategy: Existing data takes precedence on conflicts
        - Structured output: Returns Pydantic models matching input schema
        - Error handling: Automatic fallback to existing item on failure

    Performance:
        - Without batching: N duplicate items = N API calls
        - With batching: N duplicate items = O(log N) API calls
        - Typical speedup: 10-100x reduction in API calls

    Use case: Preserving historical/canonical data while augmenting with new info.
    Ideal for scenarios where existing data is authoritative but incomplete.

    Example:
        >>> from pydantic import BaseModel
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> class User(BaseModel):
        ...     uid: str
        ...     name: str | None = None
        ...     email: str | None = None
        ...     created_at: str | None = None
        >>>
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> merger = PreferExistingMerger(
        ...     key_extractor=lambda x: x.uid,
        ...     llm_client=llm,
        ...     item_schema=User,
        ... )
        >>>
        >>> items = [
        ...     User(uid="u1", name="Alice", email="alice@old.com", created_at="2024-01-01"),
        ...     User(uid="u1", name="Alicia", email="alice@new.com", created_at=None),
        ... ]
        >>>
        >>> merged = merger.merge(items)
        >>> # Result: User(uid="u1", name="Alice", email="alice@old.com", created_at="2024-01-01")
        >>> # Note: when semantic conflicts arise, existing values are preserved
    """

    def get_system_prompt(self) -> str:
        """Return the existing merge system prompt."""
        return EXISTING_PROMPT
