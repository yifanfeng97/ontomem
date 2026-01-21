"""BaseMem - Abstract base class for memory stores."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseMem(ABC, Generic[T]):
    """Abstract base class for all memory stores.

    Defines the interface that all memory implementations must follow,
    including CRUD operations, indexing, and persistence.

    Generic Parameters:
        T: The Pydantic model type for entities stored in memory.
    """

    @property
    @abstractmethod
    def keys(self) -> List[Any]:
        """Return all unique keys in memory."""
        pass

    @property
    @abstractmethod
    def items(self) -> List[T]:
        """Return all entity instances in memory."""
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        """Return the number of entities in memory."""
        pass

    @abstractmethod
    def add(self, items: Union[T, List[T]]) -> None:
        """Add item(s) to memory."""
        pass

    @abstractmethod
    def remove(self, key: Any) -> bool:
        """Remove an item by key."""
        pass

    @abstractmethod
    def get(self, key: Any) -> Optional[T]:
        """Retrieve an entity by key."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Wipe all memory."""
        pass

    @abstractmethod
    def clear_index(self) -> None:
        """Wipe the vector index."""
        pass

    @abstractmethod
    def build_index(self, force: bool = False) -> None:
        """Build/rebuild the vector index."""
        pass

    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[T]:
        """Semantic search over memory."""
        pass

    @abstractmethod
    def dump(self, folder_path: Union[str, Path]) -> None:
        """Save memory state to disk.

        Args:
            folder_path: Directory path to save memory data.
        """
        pass

    @abstractmethod
    def load(self, folder_path: Union[str, Path]) -> None:
        """Load memory state from disk.

        Args:
            folder_path: Directory path to load memory data from.
        """
        pass
