"""LLM merger that prefers incoming item values on semantic conflicts."""

from typing import TypeVar

from pydantic import BaseModel

from .base import BaseLLMMerger

T = TypeVar("T", bound=BaseModel)


INCOMING_PROMPT = """You are an expert at merging structured data intelligently.

Given two instances of the same item (identified by the same unique key), 
merge them into one complete item by combining information from both.

**Merging Rules:**
1. Keep the unique key field unchanged
2. For other fields:
   - If one has a None/empty value and the other has data, use the data
   - If both have values but they conflict semantically (both are valid but different), 
     prefer the **incoming item's value**
   - For list fields, combine both lists and remove duplicates
3. Goal: Create the most complete merged item

**Instructions:**
Merge the items intelligently. When semantic conflicts arise, choose the incoming value.
Ensure the output matches the expected schema."""


class PreferIncomingMerger(BaseLLMMerger[T]):
    """LLM merger that prefers incoming item values when semantic conflicts arise.

    Merges information from both items, combining data to create a complete result.
    When semantic conflicts occur (both items have valid but different values), 
    the incoming item's value is preferred.

    Key Features:
        - Batch optimization: Minimizes LLM API calls via tournament algorithm
        - Latest-first strategy: Incoming data takes precedence on conflicts
        - Structured output: Returns Pydantic models matching input schema
        - Error handling: Automatic fallback to incoming item on failure

    Performance:
        - Without batching: N duplicate items = N API calls
        - With batching: N duplicate items = O(log N) API calls
        - Typical speedup: 10-100x reduction in API calls

    Use case: Treating incoming data as "latest/best" while preserving historical gaps.
    Ideal for scenarios where newer information is preferable but old data is valuable.

    Example:
        >>> from pydantic import BaseModel
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> class User(BaseModel):
        ...     uid: str
        ...     name: str | None = None
        ...     email: str | None = None
        ...     status: str | None = None
        >>>
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> merger = PreferIncomingMerger(
        ...     key_extractor=lambda x: x.uid,
        ...     llm_client=llm,
        ...     item_schema=User,
        ... )
        >>>
        >>> items = [
        ...     User(uid="u1", name="Alice", email="alice@old.com", status="inactive"),
        ...     User(uid="u1", name="Alicia", email="alice@new.com", status="active"),
        ... ]
        >>>
        >>> merged = merger.merge(items)
        >>> # Result: User(uid="u1", name="Alicia", email="alice@new.com", status="active")
        >>> # Note: when semantic conflicts arise, incoming values are preferred
    """

    @property
    def system_prompt(self) -> str:
        """Return the incoming merge system prompt."""
        return INCOMING_PROMPT
