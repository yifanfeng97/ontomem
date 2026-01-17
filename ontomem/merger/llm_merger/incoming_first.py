"""LLM merger that prioritizes incoming item values."""

from typing import TypeVar

from pydantic import BaseModel

from .base import BaseLLMMerger

T = TypeVar("T", bound=BaseModel)


INCOMING_FIRST_PROMPT = """You are an expert at merging structured data intelligently.

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

**Item A (existing):**
{item_existing}

**Item B (incoming):**
{item_incoming}

**Instructions:**
Merge the items intelligently. On semantic conflicts, choose the incoming value.
Ensure the output matches the expected schema."""


class IncomingFirstMerger(BaseLLMMerger[T]):
    """LLM merger that prioritizes incoming item values on conflicts.

    Merges information from both items, combining data to create a complete result.
    When conflicts occur (both items have valid values), the incoming item wins.

    Key Features:
        - Batch optimization: Minimizes LLM API calls via tournament algorithm
        - Latest-first strategy: Incoming data takes precedence
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
        >>> merger = IncomingFirstMerger(
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
        >>> # Note: incoming values win on conflicts, but all info is merged
    """

    def get_system_prompt(self) -> str:
        """Return the incoming-first merge system prompt."""
        return INCOMING_FIRST_PROMPT
