"""Unit tests for ontomem core functionality."""

import pytest
from pydantic import BaseModel
from ontomem import OMem
from ontomem.merger import MergeStrategy


class SimpleItem(BaseModel):
    """Simple test item."""

    item_id: str
    name: str | None = None
    value: int | None = None


class TestOMem:
    """Test OMem Stateful Memory Store."""

    def test_init_basic(self):
        """Test basic initialization."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        assert memory.size == 0
        assert memory.keys == []
        assert memory.items == []

    def test_add_single_item(self):
        """Test adding a single item."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        item = SimpleItem(item_id="1", name="Alice", value=10)
        memory.add(item)

        assert memory.size == 1
        assert memory.get("1") == item

    def test_add_multiple_items(self):
        """Test adding multiple items."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        items = [
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ]
        memory.add(items)

        assert memory.size == 2
        assert memory.get("1").name == "Alice"
        assert memory.get("2").name == "Bob"

    def test_keep_incoming_strategy(self):
        """Test keep_incoming strategy on duplicate."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.KEEP_NEW
        )
        memory.add(SimpleItem(item_id="1", name="Alice", value=10))
        memory.add(SimpleItem(item_id="1", name="Bob", value=20))

        assert memory.size == 1
        item = memory.get("1")
        assert item.name == "Bob"
        assert item.value == 20

    def test_keep_existing_strategy(self):
        """Test keep_existing strategy on duplicate."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.KEEP_OLD
        )
        memory.add(SimpleItem(item_id="1", name="Alice", value=10))
        memory.add(SimpleItem(item_id="1", name="Bob", value=20))

        assert memory.size == 1
        item = memory.get("1")
        assert item.name == "Alice"
        assert item.value == 10

    def test_field_merge_strategy(self):
        """Test field merge strategy on duplicate."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        memory.add(SimpleItem(item_id="1", name="Alice", value=None))
        memory.add(SimpleItem(item_id="1", name=None, value=30))

        assert memory.size == 1
        item = memory.get("1")
        assert item.name == "Alice"
        assert item.value == 30

    def test_multiple_keys(self):
        """Test multiple unique keys in memory."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        items = [
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ]
        memory.add(items)

        assert memory.size == 2
        assert memory.get("1").name == "Alice"
        assert memory.get("2").name == "Bob"

    def test_empty_add(self):
        """Test adding empty list."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        memory.add([])
        assert memory.size == 0

    def test_remove_item(self):
        """Test removing an item."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        memory.add(SimpleItem(item_id="1", name="Alice", value=10))
        assert memory.size == 1

        removed = memory.remove("1")
        assert removed is True
        assert memory.size == 0
        assert memory.get("1") is None

    def test_remove_nonexistent(self):
        """Test removing nonexistent item."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        removed = memory.remove("nonexistent")
        assert removed is False

    def test_clear_memory(self):
        """Test clearing all memory."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        memory.add([
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ])
        assert memory.size == 2

        memory.clear()
        assert memory.size == 0
        assert memory.keys == []

    def test_invalid_strategy_requires_llm(self):
        """Test that LLM strategy requires LLM."""
        with pytest.raises(ValueError, match="requires llm_client"):
            OMem(
                memory_schema=SimpleItem,
                key_extractor=lambda x: x.item_id,
                merge_strategy=MergeStrategy.LLM.BALANCED,
                llm_client=None
            )

    def test_invalid_item_type(self):
        """Test adding wrong item type."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )

        class OtherItem(BaseModel):
            id: str

        with pytest.raises(TypeError, match="must be"):
            memory.add(OtherItem(id="1"))

    def test_keys_property(self):
        """Test keys property."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        memory.add([
            SimpleItem(item_id="1", name="Alice", value=10),
            SimpleItem(item_id="2", name="Bob", value=20),
        ])

        assert set(memory.keys) == {"1", "2"}

    def test_items_property(self):
        """Test items property."""
        memory = OMem(
            memory_schema=SimpleItem,
            key_extractor=lambda x: x.item_id,
            merge_strategy=MergeStrategy.FIELD_MERGE
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
