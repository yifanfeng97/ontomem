"""Custom rule LLM merger."""

from typing import Callable, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel

from .base import BaseLLMMerger


class CustomRuleMerger(BaseLLMMerger):
    """LLM merger with user-defined merge rules.

    Allows users to provide static and dynamic rules to control merge behavior.
    The rules are combined into a system prompt for the LLM.

    The `rule` should describe how to handle conflicts between 'Item A (existing)'
    and 'Item B (incoming)'. The `dynamic_rule` is a callable that can inject
    context-aware instructions at runtime, enabling adaptive merging based on
    external state (e.g., current time, environment variables, etc.).

    Example:
        >>> from datetime import datetime
        >>> 
        >>> def time_based_rule():
        ...     hour = datetime.now().hour
        ...     return f"Current hour is {hour}. Use recent data after 18:00."
        >>> 
        >>> merger = CustomRuleMerger(
        ...     key_extractor=lambda x: x.id,
        ...     llm_client=llm_client,
        ...     item_schema=Person,
        ...     rule="Prefer newer emails from incoming data. Keep existing names.",
        ...     dynamic_rule=time_based_rule
        ... )
    """

    def __init__(
        self,
        key_extractor: callable,
        llm_client: BaseChatModel,
        item_schema: type[BaseModel],
        rule: str,
        dynamic_rule: Optional[Callable[[], str]] = None,
        max_workers: int = 5,
    ):
        """Initialize custom rule LLM merger.

        Args:
            key_extractor: Function to extract unique key from items.
            llm_client: LangChain chat model client.
            item_schema: Pydantic model schema for items.
            rule: Static string defining the core merge logic and rules.
            dynamic_rule: Optional callable that returns a string with runtime-specific
                         rules or context. Called each time system_prompt is accessed.
            max_workers: Maximum concurrency for LLM batch calls. Defaults to 5.

        Raises:
            TypeError: If rule is not a string.
            TypeError: If dynamic_rule is provided but not callable.
        """
        super().__init__(key_extractor, llm_client, item_schema, max_workers)

        if not isinstance(rule, str):
            raise TypeError(f"rule must be str, got {type(rule)}")

        if dynamic_rule is not None and not callable(dynamic_rule):
            raise TypeError(f"dynamic_rule must be callable, got {type(dynamic_rule)}")

        self.rule = rule
        self.dynamic_rule = dynamic_rule

    @property
    def system_prompt(self) -> str:
        """Return the complete system prompt.

        Combines a standard prefix with the static rule and dynamic rule output (if any).
        The dynamic rule is evaluated each time this property is accessed, allowing
        the prompt to adapt to runtime state changes.

        Returns:
            Formatted system prompt string.
        """
        # 1. Start with role definition
        prompt = """You are an expert at merging structured data intelligently.

Given two instances of the same item (identified by the same unique key), 
merge them into one complete item by combining information from both.

**Merging Rules:**\n"""

        # 2. Add static merge rule
        prompt += self.rule

        # 3. Append dynamic rule if provided and returns non-empty string
        if self.dynamic_rule:
            dynamic_text = self.dynamic_rule()
            if dynamic_text and dynamic_text.strip():
                prompt += f"\n\nContext/Dynamic Rules:\n{dynamic_text}"

        return prompt
