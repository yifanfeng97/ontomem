"""Unit tests for incremental index maintenance (remove_many / upsert / sync_index)."""

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
    """Deterministic offline embedder (hash-based vectors)."""

    def __init__(self, dim: int = 64):
        self.dim = dim

    def _vec(self, text: str) -> list[float]:
        h = abs(hash(text))
        return [(h + i) % 1000 / 1000.0 for i in range(self.dim)]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)


def _memory() -> OMem:
    return OMem(
        memory_schema=Doc,
        key_extractor=lambda x: x.doc_id,
        llm_client=None,
        embedder=_HashEmbedder(),
        strategy_or_merger=MergeStrategy.MERGE_FIELD,
    )


class TestRemoveMany:
    def test_reports_removed_and_missing(self):
        m = _memory()
        m.add([Doc(doc_id="a", title="A"), Doc(doc_id="b", title="B")])

        removed, not_found = m.remove_many(["a", "ghost"])

        assert removed == ["a"]
        assert not_found == ["ghost"]
        assert m.get("a") is None
        assert m.get("b") is not None

    def test_does_not_clear_built_index(self):
        m = _memory()
        m.add([Doc(doc_id="a", title="A")])
        m.build_index()
        assert m.has_index()

        m.remove_many(["a"])

        # Contract: batch APIs leave the index in place; sync_index updates it.
        assert m.has_index()


class TestUpsert:
    def test_replaces_existing_without_merge(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="old", content="v1"))

        m.upsert(Doc(doc_id="a", title="new", content="v2"))

        item = m.get("a")
        assert item.title == "new"
        assert item.content == "v2"

    def test_new_key_inserts(self):
        m = _memory()
        m.upsert(Doc(doc_id="a", title="A"))

        assert m.get("a") is not None

    def test_rejects_wrong_schema(self):
        m = _memory()

        class Other(BaseModel):
            x: int

        with pytest.raises(TypeError):
            m.upsert(Other(x=1))

    def test_does_not_clear_built_index(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))
        m.build_index()

        m.upsert(Doc(doc_id="a", title="A2"))

        assert m.has_index()


class TestSyncIndex:
    def test_patches_in_place(self):
        m = _memory()
        m.add([Doc(doc_id="a", title="A"), Doc(doc_id="b", title="B")])
        m.build_index()
        removed, _ = m.remove_many(["a"])
        m.upsert(Doc(doc_id="b", title="B2"))

        ok = m.sync_index(removed_keys=removed, upserted_keys=["b"])

        assert ok is True
        assert m.has_index()
        keys = {d.metadata["key"] for d in m._index.docstore._dict.values()}
        assert keys == {"b"}
        doc = next(
            d for d in m._index.docstore._dict.values() if d.metadata["key"] == "b"
        )
        assert "B2" in doc.page_content

    def test_no_index_returns_false(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))

        assert m.sync_index(removed_keys=["a"]) is False

    def test_failure_drops_index_for_lazy_rebuild(self, monkeypatch):
        m = _memory()
        m.add([Doc(doc_id="a", title="A"), Doc(doc_id="b", title="B")])
        m.build_index()

        def boom(ids):
            raise RuntimeError("boom")

        monkeypatch.setattr(m._index, "delete", boom)
        removed, _ = m.remove_many(["a"])

        ok = m.sync_index(removed_keys=removed)

        assert ok is False
        assert not m.has_index()
        # The documented fallback: full rebuild restores a consistent index.
        m.build_index()
        assert m.has_index()
        assert m.get("a") is None

    def test_reattached_index_is_persisted_by_dump_index(self, tmp_path):
        m = _memory()
        m.add([Doc(doc_id="a", title="A"), Doc(doc_id="b", title="B")])
        m.build_index()
        removed, _ = m.remove_many(["a"])
        m.sync_index(removed_keys=removed)

        m.dump_index(str(tmp_path))

        reloaded = _memory()
        reloaded.load_index(str(tmp_path))
        keys = {d.metadata["key"] for d in reloaded._index.docstore._dict.values()}
        assert keys == {"b"}
