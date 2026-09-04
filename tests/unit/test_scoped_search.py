"""Unit tests for scoped search (source_ids / tags allowlists)."""

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


def _memory() -> OMem:
    return OMem(
        memory_schema=Doc,
        key_extractor=lambda x: x.doc_id,
        llm_client=None,
        embedder=_HashEmbedder(),
        strategy_or_merger=MergeStrategy.MERGE_FIELD,
        track_sources=True,
    )


def _seed(m: OMem):
    # two attributed sources, two items each
    m.record_source("s1", [Doc(doc_id="d1", title="D1").model_dump()], content_hash="h1")
    m.record_source("s2", [Doc(doc_id="d2", title="D2").model_dump()], content_hash="h2")
    m.add([Doc(doc_id="d1", title="D1"), Doc(doc_id="d2", title="D2")])
    m.tag_source("s1", add=["legal"])


def _query_all(m: OMem) -> list[str]:
    # a query that matches everything via hash-embedder is unreliable; fetch
    # the full docstore instead and derive from keys
    return sorted(d.metadata["key"] for d in m._index.docstore._dict.values())


class TestScopedSearch:
    def test_search_scoped_by_source(self):
        m = _memory()
        _seed(m)
        m.build_index()

        # scope to s1: d1 in, d2 out
        items = m.search("anything", top_k=10, source_ids=["s1"])
        assert [i.doc_id for i in items] == ["d1"]

    def test_search_scoped_by_tags(self):
        m = _memory()
        _seed(m)
        m.build_index()

        items = m.search("anything", top_k=10, tags=["legal"])
        assert [i.doc_id for i in items] == ["d1"]

        items = m.search("anything", top_k=10, tags=["nonexistent"])
        assert items == []

    def test_search_scoped_union_of_sources_and_tags(self):
        m = _memory()
        _seed(m)
        m.build_index()

        items = m.search("anything", top_k=10, source_ids=["s2"], tags=["legal"])
        assert sorted(i.doc_id for i in items) == ["d1", "d2"]
