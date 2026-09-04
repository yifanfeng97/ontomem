"""Unit tests for OMem.edit (LLM-assisted single-item semantic editing)."""

import pytest
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import Runnable
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


class _FakeChatModel:
    """Chat-model stub whose structured-output runnable returns canned items.

    The rewriter receives the rendered prompt text so tests can assert on
    what the editor would have seen.
    """

    def __init__(self, rewriter):
        self._rewriter = rewriter
        self.seen_text = []

    def with_structured_output(self, schema):
        model = self

        class _Runnable(Runnable):
            def invoke(self, input, config=None, **kwargs):
                text = str(input)
                model.seen_text.append(text)
                return model._rewriter(schema, text)

        return _Runnable()


def _memory() -> OMem:
    return OMem(
        memory_schema=Doc,
        key_extractor=lambda x: x.doc_id,
        llm_client=None,
        embedder=_HashEmbedder(),
        strategy_or_merger=MergeStrategy.MERGE_FIELD,
    )


def _rewritten(schema, _text):
    return schema(doc_id="a", title="A2", content="A is in Y.")


class TestEdit:
    def test_applies_rewrite(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A", content="A was founded by X."))
        m.edit(
            "a",
            remove_fact="founded by X",
            editor=_FakeChatModel(_rewritten),
        )

        item = m.get("a")
        assert item.title == "A2"
        assert item.content == "A is in Y."

    def test_prompt_contains_item_key_and_target(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A", content="hello"))
        seen = []

        def rewriter(schema, text):
            seen.append(text)
            return schema(doc_id="a", title="A", content="hello")

        m.edit("a", remove_fact="founded by X", editor=_FakeChatModel(rewriter))

        assert len(seen) == 1
        assert '"a"' in seen[0] and "hello" in seen[0] and "founded by X" in seen[0]

    def test_dry_run_does_not_apply(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A", content="old"))
        m.edit(
            "a",
            instruction="rewrite it",
            editor=_FakeChatModel(_rewritten),
            dry_run=True,
        )

        assert m.get("a").content == "old"

    def test_unchanged_rewrite_reports_no_change(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A", content="same"))

        def unchanged(schema, _text):
            return schema(doc_id="a", title="A", content="same")

        report = m.edit(
            "a", remove_fact="not present", editor=_FakeChatModel(unchanged)
        )

        assert report["changed"] is False
        assert report["applied"] is False

    def test_key_change_is_rejected_and_storage_untouched(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))

        def renamed(schema, _text):
            return schema(doc_id="renamed", title="A")

        with pytest.raises(ValueError, match="key changed"):
            m.edit("a", remove_fact="x", editor=_FakeChatModel(renamed))

        assert m.get("a") is not None
        assert m.get("renamed") is None

    def test_missing_key_raises(self):
        m = _memory()
        with pytest.raises(KeyError):
            m.edit("nope", remove_fact="x", editor=_FakeChatModel(_rewritten))

    def test_remove_fact_and_instruction_are_exclusive(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))
        with pytest.raises(ValueError, match="exactly one"):
            m.edit("a", remove_fact="a", instruction="b", editor=_FakeChatModel(_rewritten))
        with pytest.raises(ValueError, match="exactly one"):
            m.edit("a", editor=_FakeChatModel(_rewritten))

    def test_no_llm_raises(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))
        with pytest.raises(RuntimeError, match="LLM"):
            m.edit("a", remove_fact="x")


class TestEditIndexIntegration:
    def test_index_vector_refreshed_after_edit(self):
        m = _memory()
        m.add(Doc(doc_id="a", title="A", content="A was founded by X."))
        m.build_index()

        m.edit(
            "a",
            remove_fact="founded by X",
            editor=_FakeChatModel(_rewritten),
        )

        assert m.has_index()
        doc = next(
            d for d in m._index.docstore._dict.values() if d.metadata["key"] == "a"
        )
        assert "founded by X" not in doc.page_content
        assert "A is in Y." in doc.page_content

    def test_edit_failure_keeps_index(self, monkeypatch):
        m = _memory()
        m.add(Doc(doc_id="a", title="A"))
        m.build_index()

        def renamed(schema, _text):
            return schema(doc_id="renamed", title="A")

        with pytest.raises(ValueError):
            m.edit("a", remove_fact="x", editor=_FakeChatModel(renamed))

        assert m.has_index()
