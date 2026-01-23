"""Unit tests for OMem core functionality."""
import pytest
from pydantic import BaseModel
from ontomem import OMem
from ontomem.merger import MergeStrategy


class SimpleItem(BaseModel):
    item_id: str
    name: str | None = None
    value: int | None = None


@pytest.fixture
def memory():
    """Fixture: Basic OMem instance with MERGE_FIELD strategy."""
    return OMem(
        memory_schema=SimpleItem,
        key_extractor=lambda x: x.item_id,
        llm_client=None,  # Use non-LLM strategy
        embedder=None,
        strategy_or_merger=MergeStrategy.MERGE_FIELD
    )


class TestOMemBasicOperations:
    """Test basic CRUD operations."""

    def test_init_empty(self, memory):
        """Test initialization creates empty memory."""
        assert memory.size == 0
        assert memory.keys == []
        assert memory.items == []
        assert memory.empty() is True

    def test_empty_method(self, memory):
        """Test empty method."""
        # Initially empty
        assert memory.empty() is True
        
        # After adding, not empty
        memory.add(SimpleItem(item_id="1", name="Alice"))
        assert memory.empty() is False
        assert memory.size == 1
        
        # After removing, empty again
        memory.remove("1")
        assert memory.empty() is True
        assert memory.size == 0
        
        # After clearing, empty
        memory.add([
            SimpleItem(item_id="1", name="Alice"),
            SimpleItem(item_id="2", name="Bob"),
        ])
        assert memory.empty() is False
        memory.clear()
        assert memory.empty() is True

    def test_has_index(self, memory):
        """Test has_index method."""
        # Initially no index
        assert memory.has_index() is False
        
        # Manually set _index to simulate index being built
        # (we don't build actual index here to avoid needing embedder)
        from langchain_community.vectorstores import FAISS
        
        # Create a dummy document list
        from langchain_core.documents import Document as LCDocument
        dummy_docs = [
            LCDocument(page_content="test1", metadata={"key": "1"}),
            LCDocument(page_content="test2", metadata={"key": "2"}),
        ]
        
        # For testing purposes, we'll skip the actual index building
        # and just test the has_index() method's logic
        assert memory.has_index() is False
        
        # Now set _index directly for testing
        memory._index = True  # Using a truthy value to avoid needing FAISS
        assert memory.has_index() is True
        
        # Clear index
        memory._index = None
        assert memory.has_index() is False

    def test_add_single_item(self, memory):
        """Test adding a single item."""
        item = SimpleItem(item_id="1", name="Alice", value=10)
        memory.add(item)
        assert memory.size == 1
        assert memory.get("1") == item

    def test_add_multiple_items(self, memory):
        """Test adding multiple items at once."""
        items = [
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ]
        memory.add(items)
        assert memory.size == 2
        assert memory.get("1").name == "Alice"
        assert memory.get("2").name == "Bob"

    def test_add_empty_list(self, memory):
        """Test adding empty list does nothing."""
        memory.add([])
        assert memory.size == 0

    def test_get_nonexistent_key(self, memory):
        """Test getting non-existent key returns None."""
        assert memory.get("999") is None

    def test_remove_item(self, memory):
        """Test removing an item."""
        item = SimpleItem(item_id="1", name="Alice")
        memory.add(item)
        assert memory.size == 1
        memory.remove("1")
        assert memory.size == 0

    def test_remove_nonexistent(self, memory):
        """Test removing non-existent item returns False."""
        result = memory.remove("999")
        assert result is False

    def test_clear_memory(self, memory):
        """Test clearing all items."""
        memory.add([
            SimpleItem(item_id="1", name="Alice"),
            SimpleItem(item_id="2", name="Bob"),
        ])
        assert memory.size == 2
        memory.clear()
        assert memory.size == 0
        assert memory.keys == []


class TestOMemKeyExtraction:
    """Test key extraction and ID handling."""

    def test_keys_property(self, memory):
        """Test keys property returns all keys."""
        memory.add([
            SimpleItem(item_id="a", name="Alice"),
            SimpleItem(item_id="b", name="Bob"),
        ])
        assert set(memory.keys) == {"a", "b"}

    def test_items_property(self, memory):
        """Test items property returns all items."""
        item1 = SimpleItem(item_id="1", name="Alice")
        item2 = SimpleItem(item_id="2", name="Bob")
        memory.add([item1, item2])

        items = memory.items
        assert len(items) == 2
        assert item1 in items
        assert item2 in items

    def test_custom_key_extractor(self):
        """Test with custom key extractor (e.g., email instead of ID)."""
        class User(BaseModel):
            email: str
            name: str

        mem = OMem(
            memory_schema=User,
            key_extractor=lambda x: x.email,
            llm_client=None,
            embedder=None,
            strategy_or_merger=MergeStrategy.MERGE_FIELD
        )

        user = User(email="alice@example.com", name="Alice")
        mem.add(user)
        assert mem.get("alice@example.com") == user


class TestOMemTypeValidation:
    """Test type checking and validation."""

    def test_invalid_item_type(self, memory):
        """Test adding wrong type raises TypeError."""
        with pytest.raises(TypeError):
            memory.add({"item_id": "1", "name": "Alice"})  # dict, not SimpleItem

    def test_invalid_item_in_batch(self, memory):
        """Test adding batch with one invalid item raises TypeError."""
        with pytest.raises(TypeError):
            memory.add([
                SimpleItem(item_id="1", name="Alice"),
                "invalid_string",  # Wrong type
            ])
