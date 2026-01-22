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
    def search(self, query: str, top_k: int = 5) -> List[T]:
        """Semantic search over memory."""
        pass

    # --- Fine-grained Persistence (v0.1.5+) ---

    @abstractmethod
    def dump_data(self, filename: Union[str, Path]) -> None:
        """Save structured data to a JSON file (data only).

        Args:
            filename: File path to save the data (e.g., "memory.json").
        """
        pass

    @abstractmethod
    def dump_index(self, folder_path: Union[str, Path]) -> None:
        """Save vector index to a folder.

        Args:
            folder_path: Folder path where index files will be saved.
        """
        pass

    @abstractmethod
    def load_data(self, filename: Union[str, Path]) -> None:
        """Load structured data from a JSON file.

        Args:
            filename: File path to load the data from.
        """
        pass

    @abstractmethod
    def load_index(self, folder_path: Union[str, Path]) -> None:
        """Load vector index from a folder.

        Args:
            folder_path: Folder path containing index files.
        """
        pass

    @abstractmethod
    def dump_metadata(self, filename: Union[str, Path]) -> None:
        """Save metadata to a JSON file.

        Args:
            filename: File path to save metadata.
        """
        pass

    @abstractmethod
    def load_metadata(self, filename: Union[str, Path]) -> None:
        """Load metadata from a JSON file.

        Args:
            filename: File path to load metadata from.
        """
        pass

    # --- Convenience Methods ---

    def dump(self, folder_path: Union[str, Path]) -> None:
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

    def load(self, folder_path: Union[str, Path]) -> None:
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
