"""Test suite for the Lookups (Secondary Indices) feature."""

import pytest
from unittest.mock import Mock
from pydantic import BaseModel

from ontomem import OMem, MergeStrategy


class Event(BaseModel):
    """Example entity for testing Lookups."""
    id: str
    char_name: str
    location: str
    content: str
    timestamp: str


@pytest.fixture
def memory():
    """Create a test OMem instance with mock clients."""
    return OMem(
        memory_schema=Event,
        key_extractor=lambda x: x.id,
        llm_client=Mock(),
        embedder=Mock(),
        strategy_or_merger=MergeStrategy.MERGE_FIELD
    )


class TestLookupsBasic:
    """Tests for basic Lookup creation and retrieval."""

    def test_create_lookup(self, memory):
        """Test creating a lookup."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        assert "by_name" in memory.list_lookups()

    def test_create_multiple_lookups(self, memory):
        """Test creating multiple lookups."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        memory.create_lookup("by_location", lambda x: x.location)
        
        lookups = memory.list_lookups()
        assert len(lookups) == 2
        assert "by_name" in lookups
        assert "by_location" in lookups

    def test_query_by_lookup(self, memory):
        """Test querying by lookup key."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        
        events = [
            Event(id="evt_001", char_name="Alice", location="Kitchen", 
                  content="Cooking", timestamp="08:00"),
            Event(id="evt_002", char_name="Bob", location="Kitchen", 
                  content="Eating", timestamp="08:30"),
            Event(id="evt_003", char_name="Alice", location="LivingRoom", 
                  content="Watching TV", timestamp="12:00"),
        ]
        memory.add(events)
        
        # Query
        alice_events = memory.get_by_lookup("by_name", "Alice")
        assert len(alice_events) == 2
        assert all(e.char_name == "Alice" for e in alice_events)

    def test_query_by_different_lookups(self, memory):
        """Test querying by different lookup dimensions."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        memory.create_lookup("by_location", lambda x: x.location)
        
        events = [
            Event(id="evt_001", char_name="Alice", location="Kitchen", 
                  content="Cooking", timestamp="08:00"),
            Event(id="evt_002", char_name="Bob", location="Kitchen", 
                  content="Eating", timestamp="08:30"),
            Event(id="evt_003", char_name="Alice", location="LivingRoom", 
                  content="Watching TV", timestamp="12:00"),
        ]
        memory.add(events)
        
        # Query by name
        alice_events = memory.get_by_lookup("by_name", "Alice")
        assert len(alice_events) == 2
        
        # Query by location
        kitchen_events = memory.get_by_lookup("by_location", "Kitchen")
        assert len(kitchen_events) == 2

    def test_query_nonexistent_key(self, memory):
        """Test querying a non-existent key."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        events = [Event(id="evt_001", char_name="Alice", location="Kitchen", 
                       content="Cooking", timestamp="08:00")]
        memory.add(events)
        
        results = memory.get_by_lookup("by_name", "NonExistent")
        assert results == []

    def test_query_nonexistent_lookup(self, memory):
        """Test querying a non-existent lookup."""
        results = memory.get_by_lookup("nonexistent", "value")
        assert results == []


class TestLookupsMerge:
    """Tests for Lookups consistency during merge operations (critical)."""

    def test_merge_updates_lookup_single_field(self, memory):
        """Test that merge updates lookup when a field changes."""
        memory.create_lookup("by_location", lambda x: x.location)
        
        # Add initial event
        evt1 = Event(id="evt_001", char_name="Alice", location="Kitchen",
                    content="Cooking", timestamp="08:00")
        memory.add(evt1)
        
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 1
        assert len(memory.get_by_lookup("by_location", "LivingRoom")) == 0
        
        # Add same ID with different location (triggers merge)
        evt1_updated = Event(id="evt_001", char_name="Alice", location="LivingRoom",
                            content="Watching TV", timestamp="12:00")
        memory.add(evt1_updated)
        
        # Verify lookup consistency
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 0, \
            "Old lookup entry should be removed"
        assert len(memory.get_by_lookup("by_location", "LivingRoom")) == 1, \
            "New lookup entry should be added"
        
        # Verify storage is updated
        stored = memory.get("evt_001")
        assert stored.location == "LivingRoom"

    def test_merge_updates_multiple_lookups(self, memory):
        """Test that merge updates all affected lookups."""
        memory.create_lookup("by_location", lambda x: x.location)
        memory.create_lookup("by_name", lambda x: x.char_name)
        
        # Add initial event
        evt1 = Event(id="evt_001", char_name="Alice", location="Kitchen",
                    content="Cooking", timestamp="08:00")
        memory.add(evt1)
        
        # Merge with both fields changed
        evt1_updated = Event(id="evt_001", char_name="Alicia", location="Garden",
                            content="Gardening", timestamp="14:00")
        memory.add(evt1_updated)
        
        # Both lookups should be updated
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 0
        assert len(memory.get_by_lookup("by_location", "Garden")) == 1
        assert len(memory.get_by_lookup("by_name", "Alice")) == 0
        assert len(memory.get_by_lookup("by_name", "Alicia")) == 1

    def test_merge_preserves_other_items(self, memory):
        """Test that merge doesn't affect other items in lookups."""
        memory.create_lookup("by_location", lambda x: x.location)
        
        events = [
            Event(id="evt_001", char_name="Alice", location="Kitchen",
                 content="Cooking", timestamp="08:00"),
            Event(id="evt_002", char_name="Bob", location="Kitchen",
                 content="Eating", timestamp="08:30"),
        ]
        memory.add(events)
        
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 2
        
        # Update one event
        evt1_updated = Event(id="evt_001", char_name="Alice", location="LivingRoom",
                            content="Watching TV", timestamp="12:00")
        memory.add(evt1_updated)
        
        # Other item should still be in Kitchen lookup
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 1
        assert memory.get_by_lookup("by_location", "Kitchen")[0].id == "evt_002"


class TestLookupsRemove:
    """Tests for Lookups cleanup when removing items."""

    def test_remove_cleans_lookup(self, memory):
        """Test that removing an item cleans it from all lookups."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        memory.create_lookup("by_location", lambda x: x.location)
        
        event = Event(id="evt_001", char_name="Alice", location="Kitchen",
                     content="Cooking", timestamp="08:00")
        memory.add(event)
        
        assert len(memory.get_by_lookup("by_name", "Alice")) == 1
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 1
        
        # Remove event
        memory.remove("evt_001")
        
        # Item should be removed from all lookups
        assert len(memory.get_by_lookup("by_name", "Alice")) == 0
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 0

    def test_remove_preserves_other_items(self, memory):
        """Test that removing one item doesn't affect other items in lookups."""
        memory.create_lookup("by_location", lambda x: x.location)
        
        events = [
            Event(id="evt_001", char_name="Alice", location="Kitchen",
                 content="Cooking", timestamp="08:00"),
            Event(id="evt_002", char_name="Bob", location="Kitchen",
                 content="Eating", timestamp="08:30"),
        ]
        memory.add(events)
        
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 2
        
        # Remove one event
        memory.remove("evt_001")
        
        # Other item should still be in lookup
        assert len(memory.get_by_lookup("by_location", "Kitchen")) == 1
        assert memory.get_by_lookup("by_location", "Kitchen")[0].id == "evt_002"


class TestLookupsEdgeCases:
    """Tests for edge cases and error handling."""

    def test_duplicate_lookup_creation(self, memory):
        """Test that creating duplicate lookup raises error."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        
        with pytest.raises(ValueError):
            memory.create_lookup("by_name", lambda x: x.char_name)

    def test_drop_lookup(self, memory):
        """Test dropping a lookup."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        assert "by_name" in memory.list_lookups()
        
        removed = memory.drop_lookup("by_name")
        assert removed is True
        assert "by_name" not in memory.list_lookups()

    def test_drop_nonexistent_lookup(self, memory):
        """Test dropping a non-existent lookup."""
        removed = memory.drop_lookup("nonexistent")
        assert removed is False

    def test_list_lookups_empty(self, memory):
        """Test listing lookups when none exist."""
        assert memory.list_lookups() == []

    def test_reindex_existing_data(self, memory):
        """Test that creating lookup re-indexes existing data."""
        events = [
            Event(id="evt_001", char_name="Alice", location="Kitchen",
                 content="Cooking", timestamp="08:00"),
            Event(id="evt_002", char_name="Bob", location="Kitchen",
                 content="Eating", timestamp="08:30"),
        ]
        memory.add(events)
        
        # Create lookup after adding data
        memory.create_lookup("by_name", lambda x: x.char_name)
        
        # Should find existing items
        alice_events = memory.get_by_lookup("by_name", "Alice")
        assert len(alice_events) == 1
        assert alice_events[0].id == "evt_001"


class TestLookupsComposite:
    """Tests for complex scenarios with multiple lookups."""

    def test_multiple_items_same_key(self, memory):
        """Test multiple items with same lookup key."""
        memory.create_lookup("by_location", lambda x: x.location)
        
        events = [
            Event(id="evt_001", char_name="Alice", location="Kitchen",
                 content="Cooking", timestamp="08:00"),
            Event(id="evt_002", char_name="Bob", location="Kitchen",
                 content="Eating", timestamp="08:30"),
            Event(id="evt_003", char_name="Charlie", location="Kitchen",
                 content="Cleanup", timestamp="10:00"),
        ]
        memory.add(events)
        
        kitchen = memory.get_by_lookup("by_location", "Kitchen")
        assert len(kitchen) == 3
        assert all(e.location == "Kitchen" for e in kitchen)

    def test_composite_key(self, memory):
        """Test lookup with composite key."""
        memory.create_lookup(
            "by_location_hour",
            lambda x: f"{x.location}:{x.timestamp.split(':')[0]}"
        )
        
        events = [
            Event(id="evt_001", char_name="Alice", location="Kitchen",
                 content="Cooking", timestamp="08:30"),
            Event(id="evt_002", char_name="Bob", location="Kitchen",
                 content="Eating", timestamp="08:45"),
            Event(id="evt_003", char_name="Charlie", location="Kitchen",
                 content="Cleanup", timestamp="10:00"),
        ]
        memory.add(events)
        
        # Query composite key
        kitchen_8am = memory.get_by_lookup("by_location_hour", "Kitchen:08")
        assert len(kitchen_8am) == 2
        
        kitchen_10am = memory.get_by_lookup("by_location_hour", "Kitchen:10")
        assert len(kitchen_10am) == 1

    def test_three_dimensional_lookup(self, memory):
        """Test lookups across three dimensions."""
        memory.create_lookup("by_name", lambda x: x.char_name)
        memory.create_lookup("by_location", lambda x: x.location)
        memory.create_lookup("by_hour", lambda x: x.timestamp.split(':')[0])
        
        events = [
            Event(id="evt_001", char_name="Alice", location="Kitchen",
                 content="Cooking", timestamp="08:30"),
            Event(id="evt_002", char_name="Alice", location="LivingRoom",
                 content="Watching TV", timestamp="12:00"),
            Event(id="evt_003", char_name="Bob", location="Kitchen",
                 content="Eating", timestamp="08:45"),
        ]
        memory.add(events)
        
        # Query each dimension
        alice = memory.get_by_lookup("by_name", "Alice")
        assert len(alice) == 2
        
        kitchen = memory.get_by_lookup("by_location", "Kitchen")
        assert len(kitchen) == 2
        
        morning = memory.get_by_lookup("by_hour", "08")
        assert len(morning) == 2
