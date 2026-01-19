"""OMem - The Core Ontology Memory Class.

A stateful, self-consolidating semantic memory store built on Pydantic schemas,
with intelligent deduplication, merging strategies, and Faiss-based vector search.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, Type, Union

from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from .base import BaseMem, T
from ..merger import BaseMerger, create_merger, MergeStrategy
from ..utils.logging import configure_logging, get_logger

from langchain_community.vectorstores import FAISS

logger = get_logger(__name__)


class OMem(BaseMem[T], Generic[T]):
    """Stateful Ontology Memory Store.

    Implements the BaseMem interface for a semantic container for structured entities
    that handles:
    1. **Deduplication**: By key extracted from entities.
    2. **Consolidation**: Merging duplicates via configurable Strategy.
    3. **Indexing**: Optional vector search via Embeddings + Faiss.

    Generic Parameters:
        T: The Pydantic model type for entities stored in memory.

    Example:
        >>> from pydantic import BaseModel
        >>> from ontomem import OMem, MergeStrategy
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>>
        >>> class UserProfile(BaseModel):
        ...     uid: str
        ...     name: str | None = None
        ...     email: str | None = None
        ...     skills: list[str] = []
        >>>
        >>> # Method 1: Simple strategy
        >>> memory = OMem(
        ...     memory_schema=UserProfile,
        ...     key_extractor=lambda x: x.uid,
        ...     llm_client=ChatOpenAI(model="gpt-4o"),
        ...     embedder=OpenAIEmbeddings(),
        ...     strategy_or_merger=MergeStrategy.MERGE_FIELD
        ... )
        >>>
        >>> # Method 2: Custom rule with dynamic context
        >>> memory = OMem(
        ...     memory_schema=UserProfile,
        ...     key_extractor=lambda x: x.uid,
        ...     llm_client=ChatOpenAI(model="gpt-4o"),
        ...     embedder=OpenAIEmbeddings(),
        ...     strategy_or_merger=MergeStrategy.LLM.CUSTOM_RULE,
        ...     rule="Merge all skills and keep the newest name",
        ...     dynamic_rule=lambda: f"Context: {__import__('datetime').datetime.now().hour}:00"
        ... )
        >>>
        >>> memory.add([
        ...     UserProfile(uid="u1", name="Alice", skills=["Python"]),
        ...     UserProfile(uid="u1", name="Alice Smith", skills=["AI"])
        ... ])
        >>>
        >>> alice = memory.get("u1")
        >>> print(alice.name)  # -> "Alice Smith" (merged)
        >>> print(alice.skills)  # -> ["Python", "AI"] (merged)
    """

    def __init__(
        self,
        memory_schema: Type[T],
        key_extractor: Callable[[T], Any],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        strategy_or_merger: Union[MergeStrategy, BaseMerger] = MergeStrategy.LLM.BALANCED,
        fields_for_index: Optional[List[str]] = None,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """Initialize the Memory Store.

        Args:
            memory_schema: The Pydantic model class defining the entity structure.
            key_extractor: Function to extract unique ID from an entity.
                           e.g., `lambda x: x.uid` or `lambda x: x.id`
            llm_client: LangChain ChatModel instance for merging strategies.
            embedder: LangChain Embeddings instance for semantic search.
            strategy_or_merger: Merge strategy definition. Can be:
                                1. A MergeStrategy enum value (e.g., MergeStrategy.LLM.BALANCED)
                                2. A pre-configured BaseMerger instance (for full control)
            fields_for_index: (Optional) List of field names to embed for search.
                               If None, entire JSON is embedded.
            verbose: Enable DEBUG logging.
            **kwargs: Additional arguments passed to create_merger() when strategy_or_merger is
                      a MergeStrategy enum. For example, rule="..." and dynamic_rule=... for
                      MergeStrategy.LLM.CUSTOM_RULE. Ignored if strategy_or_merger is a BaseMerger instance.
        """
        if verbose:
            configure_logging(level="DEBUG")

        self.memory_schema = memory_schema
        self.key_extractor = key_extractor
        self.llm_client = llm_client
        self.embedder = embedder
        self.fields_for_index = fields_for_index or []

        # 1. Merge Strategy Setup
        if isinstance(strategy_or_merger, BaseMerger):
            # Pre-configured merger instance: use directly
            if kwargs:
                logger.warning(
                    "Initialized with a Merger instance. Additional kwargs are ignored: %s",
                    list(kwargs.keys())
                )
            self._merger = strategy_or_merger
        else:
            # MergeStrategy enum: create merger with strategy and pass kwargs
            self._merger = create_merger(
                strategy=strategy_or_merger,
                key_extractor=key_extractor,
                llm_client=llm_client,
                item_schema=memory_schema,
                **kwargs,  # Pass rule, dynamic_rule, etc. to create_merger
            )

        # 2. Storage: The single source of truth
        self._storage: Dict[Any, T] = {}

        # 3. Vector Index State (LangChain FAISS wrapper)
        self._index: Optional[FAISS] = None  # FAISS vector store
        self._index_dirty: bool = False  # Lazy indexing flag

        logger.debug(
            f"OMem initialized: schema={memory_schema.__name__}, "
            f"strategy={self._merger.__class__.__name__}, "
            f"indexing=enabled"
        )

    # --- Properties ---

    @property
    def keys(self) -> List[Any]:
        """Return all unique keys in memory."""
        return list(self._storage.keys())

    @property
    def items(self) -> List[T]:
        """Return all entity instances in memory."""
        return list(self._storage.values())

    @property
    def size(self) -> int:
        """Return the number of entities in memory."""
        return len(self._storage)

    # --- CRUD Operations ---

    def add(self, items: Union[T, List[T]]) -> None:
        """Add item(s) to memory. Automatically merges duplicates by key.

        If an item with the same key already exists, the new item(s) and
        existing item are merged using the configured strategy_or_merger.

        Args:
            items: Single entity or list of entities to add.

        Raises:
            TypeError: If item is not of memory_schema type.
        """
        # Normalize to list
        if isinstance(items, BaseModel):
            items = [items]

        if not items:
            return

        # Type validation
        for item in items:
            if not isinstance(item, self.memory_schema):
                raise TypeError(
                    f"Item must be {self.memory_schema.__name__}, got {type(item).__name__}"
                )

        # Group incoming items by key
        key_to_items: Dict[Any, List[T]] = {}
        for item in items:
            key = self.key_extractor(item)
            if key not in key_to_items:
                key_to_items[key] = []
            key_to_items[key].append(item)

        # Partition: direct insert vs merge candidates
        to_insert: List[T] = []
        to_merge: List[T] = []

        for key, new_items in key_to_items.items():
            if len(new_items) == 1 and key not in self._storage:
                # Single new item with no conflict: direct insert
                to_insert.append(new_items[0])
            else:
                # Multiple items with same key or key exists: merge
                if key in self._storage:
                    to_merge.append(self._storage[key])
                to_merge.extend(new_items)

        # Batch merge
        if to_merge:
            merged_items = self._merger.merge(to_merge)
            merged_dict = {self.key_extractor(item): item for item in merged_items}
            self._storage.update(merged_dict)

        # Direct insert
        for item in to_insert:
            key = self.key_extractor(item)
            self._storage[key] = item

        # Mark index as stale
        if self._index is not None:
            self._index_dirty = True

        logger.debug(
            f"Added {len(key_to_items)} unique keys to memory (size now: {self.size})"
        )

    def remove(self, key: Any) -> bool:
        """Remove an item by key.

        Args:
            key: The unique key of the item to remove.

        Returns:
            True if removed, False if key not found.
        """
        if key in self._storage:
            del self._storage[key]
            if self._index is not None:
                self._index_dirty = True
            logger.debug(f"Removed key {key} from memory (size now: {self.size})")
            return True
        return False

    def get(self, key: Any) -> Optional[T]:
        """Retrieve an entity by key.

        Args:
            key: The unique key of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        return self._storage.get(key)

    def clear(self) -> None:
        """Wipe all memory (reset to empty state)."""
        self._storage.clear()
        self._index = None
        self._index_dirty = False
        logger.info("Memory cleared")

    # --- Search & Indexing ---

    def build_index(self, force: bool = False) -> None:
        """Build/rebuild the vector index from current memory state.

        This operation:
        1. Serializes all items as documents.
        2. Builds FAISS index via LangChain.
        3. Resets dirty flag.

        Args:
            force: If True, rebuild even if index exists. Default: False.

        Raises:
            RuntimeError: If no embedder was provided at initialization.
        """
        if self.embedder is None:
            raise RuntimeError(
                "Cannot build index: No embedder provided at initialization."
            )

        if not force and self._index is not None:
            logger.debug("Index already built, skipping rebuild")
            return

        items = self.items
        logger.info(f"Building index for {len(items)} items...")

        if not items:
            self._index = None
            self._index_dirty = False
            logger.debug("No items to index")
            return

        # 1. Serialize items as documents
        documents = []
        for item in items:
            content = self._serialize_for_embedding(item)
            key = self.key_extractor(item)
            documents.append(
                Document(
                    page_content=content,
                    metadata={"key": key, "raw": item.model_dump()},
                )
            )

        # 2. Build FAISS index
        try:
            self._index = FAISS.from_documents(documents, self.embedder)
            self._index_dirty = False
            logger.info(f"Index built successfully with {len(documents)} items")
        except ImportError:
            logger.error(
                "FAISS not available. Install with: pip install langchain-community"
            )
            raise

    def search(self, query: str, k: int = 5) -> List[T]:
        """Semantic search over memory using vector similarity.

        Automatically rebuilds index if dirty. Returns entities ranked by
        similarity (closest first).

        Args:
            query: Natural language query string.
            k: Number of results to return. Default: 5.

        Returns:
            List of entities ranked by similarity.

        Raises:
            RuntimeError: If no embedder provided at initialization.
        """
        if self.embedder is None:
            raise RuntimeError(
                "Search unavailable: No embedder provided at initialization."
            )

        # Auto-rebuild if needed
        if self._index_dirty or self._index is None:
            logger.debug("Index is dirty or not built, rebuilding before search...")
            self.build_index()

        if self._index is None:
            logger.debug("Index is empty, returning no results")
            return []

        # Search using FAISS
        try:
            docs = self._index.similarity_search(query, k=k)
            results = []

            for doc in docs:
                try:
                    key = doc.metadata.get("key")
                    if key is not None and key in self._storage:
                        results.append(self._storage[key])
                except Exception as e:
                    logger.warning(f"Failed to restore item from search result: {e}")
                    continue

            logger.debug(f"Search returned {len(results)} results for query: '{query}'")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    # --- Persistence ---

    def dump(self, folder_path: Union[str, Path]) -> None:
        """Save memory state to disk.

        Saves to the folder:
            1. Structured data (memory items) - saved as memory.json
            2. Vector index (if built) - saved as FAISS index files

        Args:
            folder_path: Directory path to save memory data.
        """
        folder_path = Path(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)

        try:
            # 1. Save structured data
            data_file = folder_path / "memory.json"
            data = [item.model_dump(mode="json") for item in self.items]
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Memory data persisted to {data_file}")

            # 2. Save metadata
            metadata_file = folder_path / "metadata.json"
            metadata = {
                "schema_name": self.memory_schema.__name__,
                "size": self.size,
                "fields_for_index": self.fields_for_index,
            }
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Metadata persisted to {metadata_file}")

            # 3. Save vector index (if available)
            if self._index is not None:
                try:
                    index_path = str(folder_path / "faiss_index")
                    self._index.save_local(index_path)
                    logger.info(f"Vector index persisted to {index_path}")
                except Exception as e:
                    logger.warning(f"Failed to save vector index: {e}")

        except Exception as e:
            logger.error(f"Failed to persist memory: {e}")
            raise

    def load(self, folder_path: Union[str, Path]) -> None:
        """Load memory state from disk.

        Loads from the folder:
            1. Structured data (memory items) - loaded from memory.json
            2. Vector index (if available) - loaded from FAISS index files

        Args:
            folder_path: Directory path to load memory data from.
        """
        folder_path = Path(folder_path)

        try:
            # 1. Load structured data
            data_file = folder_path / "memory.json"
            if not data_file.exists():
                raise FileNotFoundError(f"Memory data file not found: {data_file}")

            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = [self.memory_schema(**d) for d in data]
            self.add(items)
            logger.info(f"Memory loaded from {data_file} ({len(items)} items)")

            # 2. Load vector index (if available)
            index_path = str(folder_path / "faiss_index")
            if Path(index_path).exists():
                try:
                    self._index = FAISS.load_local(
                        index_path, self.embedder, allow_dangerous_deserialization=True
                    )
                    self._index_dirty = False
                    logger.info(f"Vector index loaded from {index_path}")
                except Exception as e:
                    logger.warning(f"Failed to load vector index: {e}")
                    self._index = None

        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            raise

    # --- Private Helpers ---

    def _serialize_for_embedding(self, item: T) -> str:
        """Convert entity to text string for embedding.

        If fields_for_index specified, includes only those fields.
        Otherwise, includes full JSON representation.
        """
        if self.fields_for_index:
            # Selective field embedding
            parts = []
            for field_name in self.fields_for_index:
                value = getattr(item, field_name, None)
                if value is not None:
                    parts.append(f"{field_name}: {value}")
            content = "\n".join(parts)
        else:
            # Full JSON (excluding None to save tokens)
            content = item.model_dump_json(exclude_none=True)

        return content
