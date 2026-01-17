"""Unit tests for merge strategies."""
import pytest
from pydantic import BaseModel
from ontomem import OMem
from ontomem.merger import MergeStrategy


class Profile(BaseModel):
    uid: str
    name: str | None = None
    skills: list[str] = []
    bio: str | None = None


class TestFieldMergeStrategy:
    """Test FIELD_MERGE strategy: non-None overwrites, lists append."""

    @pytest.fixture
    def memory(self):
        return OMem(
            memory_schema=Profile,
            key_extractor=lambda x: x.uid,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )

    def test_field_merge_overwrite_none(self, memory):
        """Test that non-None values overwrite None."""
        memory.add(Profile(uid="u1", name="Alice", skills=["Python"]))
        memory.add(Profile(uid="u1", name="Alice Smith", skills=[]))

        result = memory.get("u1")
        assert result.name == "Alice Smith"  # Updated

    def test_field_merge_list_overwrites(self, memory):
        """Test that lists are overwritten if new value is not None."""
        memory.add(Profile(uid="u1", name="Alice", skills=["Python"]))
        memory.add(Profile(uid="u1", name="Alice", skills=["AI Dev"]))

        result = memory.get("u1")
        # Non-None value overwrites, so new list replaces old
        assert result.skills == ["AI Dev"]

    def test_field_merge_preserve_existing(self, memory):
        """Test that existing values are preserved if new is None."""
        memory.add(Profile(uid="u1", name="Alice", bio="Engineer"))
        memory.add(Profile(uid="u1", name=None, bio=None))

        result = memory.get("u1")
        assert result.name == "Alice"  # Preserved
        assert result.bio == "Engineer"  # Preserved


class TestKeepNewStrategy:
    """Test KEEP_NEW strategy: latest entry wins."""

    @pytest.fixture
    def memory(self):
        return OMem(
            memory_schema=Profile,
            key_extractor=lambda x: x.uid,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.KEEP_NEW
        )

    def test_keep_new_overwrites_all(self, memory):
        """Test that new entry completely replaces old."""
        old = Profile(uid="u1", name="Alice", skills=["Python"], bio="Dev")
        new = Profile(uid="u1", name="Bob", skills=["Java"], bio=None)

        memory.add(old)
        memory.add(new)

        result = memory.get("u1")
        assert result.name == "Bob"
        assert result.skills == ["Java"]
        assert result.bio is None  # Even None overwrites


class TestKeepOldStrategy:
    """Test KEEP_OLD strategy: first entry wins."""

    @pytest.fixture
    def memory(self):
        return OMem(
            memory_schema=Profile,
            key_extractor=lambda x: x.uid,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.KEEP_OLD
        )

    def test_keep_old_ignores_new(self, memory):
        """Test that new entry is completely ignored."""
        old = Profile(uid="u1", name="Alice", skills=["Python"])
        new = Profile(uid="u1", name="Bob", skills=["Java"])

        memory.add(old)
        memory.add(new)

        result = memory.get("u1")
        assert result.name == "Alice"
        assert result.skills == ["Python"]


class TestBatchMerge:
    """Test batch merging logic."""

    @pytest.fixture
    def memory(self):
        return OMem(
            memory_schema=Profile,
            key_extractor=lambda x: x.uid,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )

    def test_batch_with_no_conflicts(self, memory):
        """Test batch add with no conflicts (all new keys)."""
        items = [
            Profile(uid="u1", name="Alice"),
            Profile(uid="u2", name="Bob"),
            Profile(uid="u3", name="Charlie"),
        ]
        memory.add(items)
        assert memory.size == 3

    def test_batch_with_internal_conflict(self, memory):
        """Test batch where two items have same ID."""
        items = [
            Profile(uid="u1", name="Alice", skills=["Python"]),
            Profile(uid="u1", name="Alice Smith", skills=["AI"]),  # Same ID
        ]
        memory.add(items)

        # Should merge before storing
        assert memory.size == 1
        result = memory.get("u1")
        assert result.name == "Alice Smith"
        # New list value overwrites old one
        assert result.skills == ["AI"]

    def test_batch_with_existing_conflict(self, memory):
        """Test batch where one item conflicts with existing data."""
        memory.add(Profile(uid="u1", name="Alice", skills=["Python"]))

        # Now add batch where one item has same ID
        memory.add([
            Profile(uid="u1", name="Alice Smith", skills=["AI"]),
            Profile(uid="u2", name="Bob", skills=[]),
        ])

        assert memory.size == 2
        assert memory.get("u1").name == "Alice Smith"
        assert memory.get("u2").name == "Bob"
