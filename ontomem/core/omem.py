"""OMem - The Core Ontology Memory Class.

A stateful, self-consolidating semantic memory store built on Pydantic schemas,
with intelligent deduplication, merging strategies, and Faiss-based vector search.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, Set, Type, Union

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
        strategy_or_merger: Union[
            MergeStrategy, BaseMerger
        ] = MergeStrategy.LLM.BALANCED,
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

        if self.fields_for_index:
            for field in self.fields_for_index:
                if field not in self.memory_schema.model_fields:
                    raise ValueError(
                        f"Field '{field}' not in memory_schema '{self.memory_schema.__name__}'"
                    )

        # 1. Merge Strategy Setup
        if isinstance(strategy_or_merger, BaseMerger):
            # Pre-configured merger instance: use directly
            if kwargs:
                logger.warning(
                    "Initialized with a Merger instance. Additional kwargs are ignored: %s",
                    list(kwargs.keys()),
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

        # 3. Lookups (Secondary Indices)
        # Structure: {lookup_name: {lookup_value: Set[primary_key]}}
        self._lookups: Dict[str, Dict[Any, Set[Any]]] = {}
        # Structure: {lookup_name: key_extractor_func}
        self._lookup_extractors: Dict[str, Callable[[T], Any]] = {}

        # 4. Vector Index State (LangChain FAISS wrapper)
        self._index: Optional[FAISS] = None  # FAISS vector store

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

    def has_index(self) -> bool:
        """Check if vector index is currently built.

        Returns:
            True if index exists, False otherwise.
        """
        return self._index is not None

    # --- Lookups (Secondary Indices) ---

    def create_lookup(self, name: str, key_extractor: Callable[[T], Any]) -> None:
        """Create a secondary lookup table for fast retrieval by custom key.

        Example:
            >>> memory.create_lookup('by_name', lambda x: x.name)
            >>> results = memory.get_by_lookup('by_name', 'Alice')

        Args:
            name: Unique name for this lookup (e.g., 'by_name', 'by_location').
            key_extractor: Function to extract the lookup key from an entity.

        Raises:
            ValueError: If lookup with this name already exists.
        """
        if name in self._lookups:
            raise ValueError(f"Lookup '{name}' already exists. Use drop_lookup() to remove it first.")

        self._lookups[name] = {}
        self._lookup_extractors[name] = key_extractor

        # Re-index existing data
        logger.debug(f"Creating lookup '{name}' with {len(self._storage)} existing items...")
        for pk, item in self._storage.items():
            self._add_to_lookup(name, pk, item)

        logger.info(f"Lookup '{name}' created successfully")

    def get_by_lookup(self, lookup_name: str, lookup_key: Any) -> List[T]:
        """Retrieve items using a secondary lookup key.

        Args:
            lookup_name: The name of the lookup table.
            lookup_key: The value to match (e.g., 'Alice', 'Kitchen').

        Returns:
            List of matching entities. Returns empty list if lookup not found or no matches.
        """
        if lookup_name not in self._lookups:
            logger.warning(f"Lookup '{lookup_name}' does not exist.")
            return []

        target_lookup = self._lookups[lookup_name]

        if lookup_key not in target_lookup:
            return []

        pks = target_lookup[lookup_key]
        results = []
        for pk in pks:
            if pk in self._storage:
                results.append(self._storage[pk])

        return results

    def drop_lookup(self, name: str) -> bool:
        """Remove a lookup table.

        Args:
            name: The name of the lookup to remove.

        Returns:
            True if removed, False if lookup not found.
        """
        if name in self._lookups:
            del self._lookups[name]
            del self._lookup_extractors[name]
            logger.info(f"Lookup '{name}' dropped")
            return True
        return False

    def list_lookups(self) -> List[str]:
        """List all registered lookup names.

        Returns:
            List of lookup names.
        """
        return list(self._lookups.keys())

    # --- Private Lookup Helpers ---

    def _add_to_lookup(self, lookup_name: str, pk: Any, item: T) -> None:
        """Helper: Add an entry to a specific lookup.

        Args:
            lookup_name: Name of the lookup.
            pk: Primary key of the item.
            item: The item to index.
        """
        try:
            extractor = self._lookup_extractors[lookup_name]
            val = extractor(item)
            if val is None:
                return

            # Ensure val is hashable
            hash(val)

            if val not in self._lookups[lookup_name]:
                self._lookups[lookup_name][val] = set()
            self._lookups[lookup_name][val].add(pk)
        except TypeError:
            logger.warning(
                f"Lookup '{lookup_name}': extracted value is not hashable. Skipping item {pk}."
            )
        except Exception as e:
            logger.warning(f"Failed to update lookup '{lookup_name}' for item {pk}: {e}")

    def _remove_from_lookup(self, lookup_name: str, pk: Any, item: T) -> None:
        """Helper: Remove an entry from a specific lookup using the item state.

        Args:
            lookup_name: Name of the lookup.
            pk: Primary key of the item.
            item: The item to de-index (used to extract the old lookup key).
        """
        try:
            extractor = self._lookup_extractors[lookup_name]
            val = extractor(item)
            if val is None:
                return

            if val in self._lookups[lookup_name]:
                if pk in self._lookups[lookup_name][val]:
                    self._lookups[lookup_name][val].remove(pk)
                    # Clean up empty keys to save memory
                    if not self._lookups[lookup_name][val]:
                        del self._lookups[lookup_name][val]
        except Exception as e:
            logger.warning(f"Failed to remove from lookup '{lookup_name}' for item {pk}: {e}")

    def _update_all_lookups(self, pk: Any, new_item: T, old_item: Optional[T] = None) -> None:
        """Update all lookups for a given primary key.

        Args:
            pk: Primary key of the item.
            new_item: The new item state.
            old_item: The old item state (optional, for removal during updates).
        """
        for name in self._lookups:
            # 1. If we have the old item, remove its trace from this lookup
            if old_item:
                self._remove_from_lookup(name, pk, old_item)

            # 2. Add the new trace
            self._add_to_lookup(name, pk, new_item)

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
            # Snapshot old items before merge for lookup cleanup
            items_to_update_keys = set()
            old_items_map: Dict[Any, T] = {}

            for item in to_merge:
                pk = self.key_extractor(item)
                if pk in self._storage:
                    items_to_update_keys.add(pk)
                    old_items_map[pk] = self._storage[pk]

            merged_items = self._merger.merge(to_merge)
            merged_dict = {self.key_extractor(item): item for item in merged_items}
            self._storage.update(merged_dict)

            # Update lookups for merged items
            for pk, new_item in merged_dict.items():
                old_item = old_items_map.get(pk)
                self._update_all_lookups(pk, new_item, old_item)

        # Direct insert
        for item in to_insert:
            pk = self.key_extractor(item)
            self._storage[pk] = item
            # Update lookups (no old item, only add)
            self._update_all_lookups(pk, item, old_item=None)

        # Mark index as stale
        if self._index is not None:
            self.clear_index()

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
            item = self._storage[key]
            # Remove from lookups first using the item state
            for name in self._lookups:
                self._remove_from_lookup(name, key, item)

            del self._storage[key]
            if self._index is not None:
                self.clear_index()
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
        self.clear_index()
        logger.info("Memory cleared")

    def clear_index(self) -> None:
        """Clear the vector index without affecting stored items."""
        self._index = None
        logger.info("Vector index cleared")

    # --- Search & Indexing ---

    def build_index(self, force: bool = False) -> None:
        """Build/rebuild the vector index from current memory state.

        This operation:
        1. Serializes all items as documents.
        2. Builds FAISS index via LangChain.

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
            logger.info(f"Index built successfully with {len(documents)} items")
        except ImportError:
            logger.error(
                "FAISS not available. Install with: pip install langchain-community"
            )
            raise

    def search(self, query: str, top_k: int = 5) -> List[T]:
        """Semantic search over memory using vector similarity.

        Automatically rebuilds index if not built. Returns entities ranked by
        similarity (closest first).

        Args:
            query: Natural language query string.
            top_k: Number of results to return. Default: 5.

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
        if self._index is None:
            logger.debug("Index is not built, rebuilding before search...")
            self.build_index()

        if self._index is None:
            logger.debug("Index is empty, returning no results")
            return []

        # Search using FAISS
        try:
            docs = self._index.similarity_search(query, k=top_k)
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

    # --- Persistence (Fine-grained v0.1.5+) ---

    def dump_data(self, file_path: Union[str, Path]) -> None:
        """Save structured data to a JSON file (data only).

        Args:
            file_path: File path to save the data (e.g., "memory.json").
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = [item.model_dump(mode="json") for item in self.items]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Memory data persisted to {file_path}")
        except Exception as e:
            logger.error(f"Failed to persist memory data: {e}")
            raise

    def dump_index(self, folder_path: Union[str, Path]) -> None:
        """Save vector index to a folder.

        Index files will be saved directly in this folder.

        Args:
            folder_path: Folder path where index files will be saved.
        """
        folder_path = Path(folder_path)

        if self._index is None:
            logger.debug("No index to save (index not built)")
            return

        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            self._index.save_local(str(folder_path))
            logger.info(f"Vector index persisted to {folder_path}")
        except Exception as e:
            logger.warning(f"Failed to save vector index: {e}")
            raise

    def load_data(self, file_path: Union[str, Path]) -> None:
        """Load structured data from a JSON file.

        Args:
            file_path: File path to load the data from.
        """
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Memory data file not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = [self.memory_schema(**d) for d in data]
            self.add(items)
            logger.info(f"Memory loaded from {file_path} ({len(items)} items)")

        except Exception as e:
            logger.error(f"Failed to load memory data: {e}")
            raise

    def load_index(self, folder_path: Union[str, Path]) -> None:
        """Load vector index from a folder.

        Args:
            folder_path: Folder path containing index files.
        """
        folder_path = Path(folder_path)

        if not folder_path.exists():
            logger.debug(f"No index folder found at {folder_path}, skipping")
            return

        try:
            self._index = FAISS.load_local(
                str(folder_path), self.embedder, allow_dangerous_deserialization=True
            )
            logger.info(f"Vector index loaded from {folder_path}")
        except Exception as e:
            logger.warning(f"Failed to load vector index: {e}")
            self._index = None
            raise

    def dump_metadata(self, file_path: Union[str, Path]) -> None:
        """Save metadata to a JSON file.

        Args:
            file_path: File path to save metadata.
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            metadata = {
                "schema_name": self.memory_schema.__name__,
                "size": self.size,
                "fields_for_index": self.fields_for_index,
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Metadata persisted to {file_path}")
        except Exception as e:
            logger.warning(f"Failed to persist metadata: {e}")

    def load_metadata(self, file_path: Union[str, Path]) -> None:
        """Load metadata from a JSON file.

        Args:
            file_path: File path to load metadata from.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.debug(f"Metadata file not found: {file_path}, skipping")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            logger.info(f"Metadata loaded from {file_path}")
            logger.debug(
                f"Schema: {metadata.get('schema_name')}, Size: {metadata.get('size')}"
            )
        except Exception as e:
            logger.warning(f"Failed to load metadata: {e}")

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
