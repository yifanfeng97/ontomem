"""Unit tests for the source ledger & provenance features (v0.4.0)."""


import pytest
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel

from ontomem import OMem
from ontomem.merger import MergeStrategy


class Doc(BaseModel):
    doc_id: str
    title: str
    content: str = ""


class _HashEmbedder(Embeddings):
    """Deterministic offline embedder."""

    def __init__(self, dim: int = 64):
        self.dim = dim

    def _vec(self, text: str) -> list[float]:
        h = abs(hash(text))
        return [(h + i) % 1000 / 1000.0 for i in range(self.dim)]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)


class _OtherEmbedder(Embeddings):
    """A different embedder class (different signature)."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.5] * 64 for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.5] * 64


def _memory(**overrides) -> OMem:
    kwargs = {
        "memory_schema": Doc,
        "key_extractor": lambda x: x.doc_id,
        "llm_client": None,
        "embedder": _HashEmbedder(),
        "strategy_or_merger": MergeStrategy.MERGE_FIELD,
        "track_sources": True,
    }
    kwargs.update(overrides)
    return OMem(**kwargs)


class TestLedgerCapture:
    def test_add_with_source_records_raw_items(self):
        m = _memory()
        m.add(
            [Doc(doc_id="a", title="A", content="from s1")],
            source_id="doc-1",
        )

        assert "doc-1" in m.sources()
        assert m.sources()["doc-1"]["raw_items"] == 1
        # Raw content is preserved in the ledger, even after merging.
        raw = m._sources["doc-1"].raw_items[0]
        assert raw["content"] == "from s1"

    def test_add_without_source_id_is_not_captured(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))

        assert m.sources() == {}

    def test_track_sources_disabled_raises_on_provenance_calls(self):
        m = _memory(track_sources=False)
        m.add(Doc(doc_id="a", title="A"))

        with pytest.raises(RuntimeError, match="track_sources"):
            m.remove_source("a")
        with pytest.raises(RuntimeError, match="track_sources"):
            m.upsert_source("a", [Doc(doc_id="b", title="B")])


class TestRemoveSource:
    def test_exact_rollback_removes_sole_contributions(self):
        m = _memory()
        m.add(Doc(doc_id="only-s1", title="S1 item"), source_id="s1")
        m.add(Doc(doc_id="shared", title="shared"), source_id="s2")

        report = m.remove_source("s1", strategy="exact")

        # "shared" survives (s2 also contributed); "only-s1" is deleted.
        assert report["removed_keys"] == ["only-s1"]
        assert report["remerged_keys"] == []
        assert "only-s1" not in m._storage
        assert "shared" in m._storage

    def test_exact_rollback_remerges_shared_keys(self):
        m = _memory()
        # s1 writes a fact into "a"; s2 later overwrites the same key.
        m.add(
            Doc(doc_id="a", title="A", content="fact from s1"),
            source_id="s1",
        )
        m.add(
            Doc(doc_id="a", title="A", content="fact from s2"),
            source_id="s2",
        )
        assert m.get("a").content == "fact from s2"  # merged view

        report = m.remove_source("s1", strategy="exact")

        # Re-merged from s2's raw result: s1's fact is gone, s2's remains.
        assert "a" in report["remerged_keys"]
        assert "fact from s1" not in m.get("a").content
        assert "fact from s2" in m.get("a").content
        # Ledger: s1 popped, s2 intact.
        assert "s1" not in m._sources
        assert "s2" in m._sources

    def test_touched_strategy_deletes_shared_keys(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"), source_id="s1")
        m.add(Doc(doc_id="a", title="A2"), source_id="s2")

        report = m.remove_source("s1", strategy="touched")

        assert report["removed_keys"] == ["a"]  # deleted outright, no re-merge
        assert "a" not in m._storage

    def test_unknown_source_raises(self):
        m = _memory()
        with pytest.raises(KeyError):
            m.remove_source("ghost")

    def test_invalid_strategy_raises(self):
        m = _memory()
        with pytest.raises(ValueError, match="strategy"):
            m.remove_source("a", strategy="nuke")

    def test_remove_source_twice_second_is_noop(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"), source_id="s1")
        m.remove_source("s1")

        with pytest.raises(KeyError):
            m.remove_source("s1")


class TestUpsertSource:
    def test_upsert_rolls_back_old_and_merges_new(self):
        m = _memory()
        m.add(Doc(doc_id="b", title="B"), source_id="s1")
        m.add(
            [
                Doc(doc_id="a", title="A", content="a fact from s1"),
                Doc(doc_id="b", title="B", content="b fact from s1"),
            ],
            source_id="s1",
        )
        # s2 contributes to "a" as well — it must survive s1's rollback.
        m.add(
            Doc(doc_id="a", title="A", content="a fact from s2"),
            source_id="s2",
        )

        report = m.upsert_source(
            "s1",
            [Doc(doc_id="a", title="A", content="a fact v2 from s1")],
            strategy="exact",
        )

        # "b" was solely s1's → deleted with the rollback.
        assert "b" in report["removed_keys"]
        assert m.get("b") is None
        # "a" survives (s2 contributed too). MERGE_FIELD scalar semantics:
        # the newest value wins, so content is s1 v2's text.
        assert m.get("a") is not None
        assert m.get("a").content == "a fact v2 from s1"
        # The rollback re-merged "a" from s2 before the new version landed —
        # provable via the report.
        assert "a" in report["remerged_keys"]
        # Ledger now holds only s1's v2 raw items.
        assert len(m._sources["s1"].raw_items) == 1
        assert m._sources["s1"].raw_items[0]["content"] == "a fact v2 from s1"

    def test_upsert_content_hash_recorded(self):
        m = _memory()
        m.upsert_source("s1", [Doc(doc_id="a", title="A")], content_hash="abc123")

        assert m.sources()["s1"]["content_hash"] == "abc123"


class TestSourcesPersistence:
    def test_dump_load_sources_roundtrip(self, tmp_path):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"), source_id="s1")
        m.add(Doc(doc_id="b", title="B"), source_id="s2")
        m.dump_data(tmp_path / "data.json")
        path = tmp_path / "sources.json"
        m.dump_sources(path)

        m2 = _memory()
        m2.load_data(tmp_path / "data.json")
        m2.load_sources(path)

        assert set(m2.sources()) == {"s1", "s2"}
        # Rollback works on the reloaded state (data + ledger together):
        # s1 only touched "a", so exactly that key is removed; s2's "b" stays.
        report = m2.remove_source("s1", strategy="touched")
        assert set(report["removed_keys"]) == {"a"}
        assert "b" in m2._storage
        assert "s2" in m2._sources


class TestSuspendedIndex:
    def test_exception_reattaches_index(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))
        m.build_index()
        assert m.has_index()

        with pytest.raises(RuntimeError, match="boom"), m.suspended_index():
            assert not m.has_index()  # detached inside
            raise RuntimeError("boom")

        assert m.has_index()  # reattached untouched


class TestEmbedderFingerprint:
    def test_dump_writes_meta_and_load_rejects_mismatch(self, tmp_path):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))
        m.build_index()
        m.dump_index(tmp_path)
        assert (tmp_path / "index.meta.json").exists()

        m2 = _memory(embedder=_OtherEmbedder())
        m2.load_index(tmp_path)
        # Mismatched embedder: index refused so vector spaces never mix.
        assert not m2.has_index()

    def test_same_embedder_loads(self, tmp_path):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))
        m.build_index()
        m.dump_index(tmp_path)

        m2 = _memory()
        m2.load_index(tmp_path)
        assert m2.has_index()
