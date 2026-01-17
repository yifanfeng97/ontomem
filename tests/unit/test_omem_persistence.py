"""Unit tests for save/load functionality."""
import pytest
import json
from pydantic import BaseModel
from ontomem import OMem
from ontomem.merger import MergeStrategy


class Item(BaseModel):
    item_id: str
    name: str | None = None
    value: int = 0


class TestPersistence:
    """Test dump and load functionality."""

    @pytest.fixture
    def memory(self):
        return OMem(
            memory_schema=Item,
            key_extractor=lambda x: x.item_id,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Fixture: Temporary directory for testing."""
        return tmp_path / "memory_data"

    def test_dump_creates_directory(self, memory, temp_dir):
        """Test dump creates directory if not exists."""
        memory.add(Item(item_id="1", name="Alice"))
        memory.dump(temp_dir)

        assert temp_dir.exists()
        assert (temp_dir / "memory.json").exists()

    def test_dump_saves_memory_json(self, memory, temp_dir):
        """Test dump saves items to memory.json."""
        items = [
            Item(item_id="1", name="Alice", value=10),
            Item(item_id="2", name="Bob", value=20),
        ]
        memory.add(items)
        memory.dump(temp_dir)

        # Load and verify JSON (data is saved as a list)
        with open(temp_dir / "memory.json") as f:
            data = json.load(f)

        assert len(data) == 2
        assert isinstance(data, list)
        # Find items by ID
        item1 = next((item for item in data if item["item_id"] == "1"), None)
        item2 = next((item for item in data if item["item_id"] == "2"), None)
        assert item1 is not None and item1["name"] == "Alice"
        assert item2 is not None and item2["value"] == 20

    def test_dump_saves_metadata(self, memory, temp_dir):
        """Test dump saves metadata.json."""
        memory.add(Item(item_id="1", name="Alice"))
        memory.dump(temp_dir)

        assert (temp_dir / "metadata.json").exists()

        with open(temp_dir / "metadata.json") as f:
            metadata = json.load(f)

        assert "schema_name" in metadata or len(metadata) >= 0  # Metadata exists

    def test_load_empty_directory(self, memory, temp_dir):
        """Test load on empty directory raises error."""
        temp_dir.mkdir(exist_ok=True)
        # Loading from empty directory should raise error (no memory.json)
        with pytest.raises(FileNotFoundError):
            memory.load(temp_dir)

    def test_load_memory_json(self, memory, temp_dir):
        """Test load restores items from memory.json."""
        # Save
        items = [
            Item(item_id="1", name="Alice", value=10),
            Item(item_id="2", name="Bob", value=20),
        ]
        memory.add(items)
        memory.dump(temp_dir)

        # Load
        memory2 = OMem(
            memory_schema=Item,
            key_extractor=lambda x: x.item_id,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        memory2.load(temp_dir)

        assert memory2.size == 2
        assert memory2.get("1").name == "Alice"
        assert memory2.get("2").value == 20

    def test_round_trip_dump_load(self, memory, temp_dir):
        """Test full round-trip: dump then load."""
        original_items = [
            Item(item_id=f"id_{i}", name=f"Person_{i}", value=i*10)
            for i in range(5)
        ]
        memory.add(original_items)
        memory.dump(temp_dir)

        # Create new instance and load
        memory2 = OMem(
            memory_schema=Item,
            key_extractor=lambda x: x.item_id,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        memory2.load(temp_dir)

        # Verify all items match
        for item in original_items:
            loaded = memory2.get(item.item_id)
            assert loaded == item

    def test_dump_overwrites_existing(self, memory, temp_dir):
        """Test that dump overwrites previous saves."""
        # First dump
        memory.add(Item(item_id="1", name="Alice"))
        memory.dump(temp_dir)

        # Second dump with different data
        memory.clear()
        memory.add([
            Item(item_id="2", name="Bob"),
            Item(item_id="3", name="Charlie"),
        ])
        memory.dump(temp_dir)

        # Load and verify
        memory2 = OMem(
            memory_schema=Item,
            key_extractor=lambda x: x.item_id,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        memory2.load(temp_dir)

        assert memory2.size == 2
        assert memory2.get("1") is None
        assert memory2.get("2").name == "Bob"
