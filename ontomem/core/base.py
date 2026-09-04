"""BaseMem - Abstract base class for memory stores."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
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
    def keys(self) -> list[Any]:
        """Return all unique keys in memory."""

    @property
    @abstractmethod
    def items(self) -> list[T]:
        """Return all entity instances in memory."""

    @property
    @abstractmethod
    def size(self) -> int:
        """Return the number of entities in memory."""

    def empty(self) -> bool:
        """Check if memory is empty.

        Returns:
            True if no entities in memory, False otherwise.
        """
        return self.size == 0

    @abstractmethod
    def has_index(self) -> bool:
        """Check if vector index has been built.

        Returns:
            True if index exists and is ready for search.
        """

    @abstractmethod
    def add(self, items: T | list[T]) -> None:
        """Add item(s) to memory."""

    @abstractmethod
    def remove(self, key: Any) -> bool:
        """Remove an item by key."""

    @abstractmethod
    def get(self, key: Any) -> T | None:
        """Retrieve an entity by key."""

    @abstractmethod
    def clear(self) -> None:
        """Wipe all memory."""

    @abstractmethod
    def clear_index(self) -> None:
        """Wipe the vector index."""

    @abstractmethod
    def build_index(self, force: bool = False) -> None:
        """Build/rebuild the vector index."""

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[T]:
        """Semantic search over memory."""

    # --- Incremental Index Maintenance & Editing (v0.3.0+) ---

    def remove_many(self, keys: list[Any]) -> tuple[list[Any], list[Any]]:
        """Remove multiple items by key without dropping the vector index.

        Pair with :meth:`sync_index` to patch the index incrementally.
        Optional: the default implementation returns empty results.
        """
        raise NotImplementedError

    def upsert(self, items: T | list[T]) -> None:
        """Insert or replace items by key, bypassing merge."""
        raise NotImplementedError

    def sync_index(
        self,
        *,
        removed_keys: list[Any] | None = None,
        upserted_keys: list[Any] | None = None,
    ) -> bool:
        """Patch the vector index in place for the affected keys.

        Returns:
            True if patched in place; False when no index is built or
            patching failed (fall back to :meth:`build_index`).
        """
        raise NotImplementedError

    def edit(
        self,
        key: Any,
        *,
        remove_fact: str | None = None,
        instruction: str | None = None,
        editor: BaseChatModel | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """LLM-assisted semantic edit of one stored item."""
        raise NotImplementedError

    # --- Fine-grained Persistence (v0.1.5+) ---

    @abstractmethod
    def dump_data(self, file_path: str | Path) -> None:
        """Save structured data to a JSON file (data only).

        Args:
            file_path: File path to save the data (e.g., "memory.json").
        """

    @abstractmethod
    def dump_index(self, folder_path: str | Path) -> None:
        """Save vector index to a folder.

        Args:
            folder_path: Folder path where index files will be saved.
        """

    @abstractmethod
    def load_data(self, file_path: str | Path) -> None:
        """Load structured data from a JSON file.

        Args:
            file_path: File path to load the data from.
        """

    @abstractmethod
    def load_index(self, folder_path: str | Path) -> None:
        """Load vector index from a folder.

        Args:
            folder_path: Folder path containing index files.
        """

    @abstractmethod
    def dump_metadata(self, file_path: str | Path) -> None:
        """Save metadata to a JSON file.

        Args:
            file_path: File path to save metadata.
        """

    @abstractmethod
    def load_metadata(self, file_path: str | Path) -> None:
        """Load metadata from a JSON file.

        Args:
            file_path: File path to load metadata from.
        """

    # --- Convenience Methods ---

    def dump(self, folder_path: str | Path) -> None:
        """Save memory state to disk (data + metadata + index).

        Saves to the folder:
            1. Structured data - memory.json
            2. Metadata - metadata.json
            3. Vector index - faiss_index/ subfolder (if built)

        Args:
            folder_path: Base directory path to save memory data.
        """
        folder_path = Path(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)

        self.dump_data(folder_path / "memory.json")
        self.dump_metadata(folder_path / "metadata.json")
        self.dump_index(folder_path / "faiss_index")

    def load(self, folder_path: str | Path) -> None:
        """Load memory state from disk (data + metadata + index).

        Loads from the folder:
            1. Structured data - memory.json
            2. Metadata - metadata.json
            3. Vector index - faiss_index/ subfolder (if available)

        Args:
            folder_path: Base directory path to load memory data from.
        """
        folder_path = Path(folder_path)

        self.load_data(folder_path / "memory.json")
        self.load_metadata(folder_path / "metadata.json")
        self.load_index(folder_path / "faiss_index")
