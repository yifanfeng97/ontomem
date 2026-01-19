"""Unit tests for ontomem core functionality."""

import pytest
from pydantic import BaseModel
from unittest.mock import Mock
from ontomem import OMem
from ontomem.merger import MergeStrategy


class SimpleItem(BaseModel):
    """Simple test item."""

    item_id: str
    name: str | None = None
    value: int | None = None


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    return Mock()


@pytest.fixture
def mock_embedder():
    """Create a mock embedder."""
    embedder = Mock()
    embedder.embed_documents = Mock(return_value=[[0.1] * 384] * 10)
    embedder.embed_query = Mock(return_value=[0.1] * 384)
    return embedder


class TestOMem:
    """Test OMem Stateful Memory Store."""

    def test_init_basic(self, mock_llm, mock_embedder):
        """Test basic initialization."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        assert memory.size == 0
        assert memory.keys == []
        assert memory.items == []

    def test_add_single_item(self, mock_llm, mock_embedder):
        """Test adding a single item."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        item = SimpleItem(item_id="1", name="Alice", value=10)
        memory.add(item)

        assert memory.size == 1
        assert memory.get("1") == item

    def test_add_multiple_items(self, mock_llm, mock_embedder):
        """Test adding multiple items."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        items = [
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ]
        memory.add(items)

        assert memory.size == 2
        assert memory.get("1").name == "Alice"
        assert memory.get("2").name == "Bob"

    def test_keep_incoming_strategy(self, mock_llm, mock_embedder):
        """Test keep_incoming strategy on duplicate."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.KEEP_INCOMING
        )
        memory.add(SimpleItem(item_id="1", name="Alice", value=10))
        memory.add(SimpleItem(item_id="1", name="Bob", value=20))

        assert memory.size == 1
        item = memory.get("1")
        assert item.name == "Bob"
        assert item.value == 20

    def test_keep_existing_strategy(self, mock_llm, mock_embedder):
        """Test keep_existing strategy on duplicate."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.KEEP_EXISTING
        )
        memory.add(SimpleItem(item_id="1", name="Alice", value=10))
        memory.add(SimpleItem(item_id="1", name="Bob", value=20))

        assert memory.size == 1
        item = memory.get("1")
        assert item.name == "Alice"
        assert item.value == 10

    def test_merge_field_strategy(self, mock_llm, mock_embedder):
        """Test field merge strategy on duplicate."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        memory.add(SimpleItem(item_id="1", name="Alice", value=None))
        memory.add(SimpleItem(item_id="1", name=None, value=30))

        assert memory.size == 1
        item = memory.get("1")
        assert item.name == "Alice"
        assert item.value == 30

    def test_multiple_keys(self, mock_llm, mock_embedder):
        """Test multiple unique keys in memory."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        items = [
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ]
        memory.add(items)

        assert memory.size == 2
        assert memory.get("1").name == "Alice"
        assert memory.get("2").name == "Bob"

    def test_empty_add(self, mock_llm, mock_embedder):
        """Test adding empty list."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        memory.add([])
        assert memory.size == 0

    def test_remove_item(self, mock_llm, mock_embedder):
        """Test removing an item."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        memory.add(SimpleItem(item_id="1", name="Alice", value=10))
        assert memory.size == 1

        removed = memory.remove("1")
        assert removed is True
        assert memory.size == 0
        assert memory.get("1") is None

    def test_remove_nonexistent(self, mock_llm, mock_embedder):
        """Test removing nonexistent item."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        removed = memory.remove("nonexistent")
        assert removed is False

    def test_clear_memory(self, mock_llm, mock_embedder):
        """Test clearing all memory."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        memory.add([
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ])
        assert memory.size == 2

        memory.clear()
        assert memory.size == 0
        assert memory.keys == []

    def test_invalid_strategy_requires_llm(self, mock_llm, mock_embedder):
        """Test that LLM strategy works with provided LLM."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.LLM.BALANCED
        )
        assert memory is not None

    def test_invalid_item_type(self, mock_llm, mock_embedder):
        """Test adding wrong item type."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )

        class OtherItem(BaseModel):
            id: str

        with pytest.raises(TypeError, match="must be"):
            memory.add(OtherItem(id="1"))

    def test_keys_property(self, mock_llm, mock_embedder):
        """Test keys property."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        memory.add([
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ])

        assert set(memory.keys) == {"1", "2"}

    def test_items_property(self, mock_llm, mock_embedder):
        """Test items property."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            llm_client=mock_llm,
            embedder=mock_embedder,
            merge_strategy=MergeStrategy.MERGE_FIELD
        )
        items = [
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ]
        memory.add(items)

        assert len(memory.items) == 2
        names = {item.name for item in memory.items}
        assert names == {"Alice", "Bob"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
