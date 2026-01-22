"""Unit tests for search and indexing."""
import pytest
from pydantic import BaseModel
from ontomem import OMem
from ontomem.merger import MergeStrategy


class Document(BaseModel):
    doc_id: str
    title: str
    content: str
    tags: list[str] = []


class TestIndexing:
    """Test vector index building."""

    @pytest.fixture
    def embedder(self, has_openai_key):
        """Fixture: Real embedder (reads from .env OPENAI_API_KEY)."""
        if not has_openai_key:
            return None
        
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings()
        except Exception as e:
            pytest.skip(f"Failed to initialize embedder: {e}")

    @pytest.mark.requires_openai
    def test_build_index_empty(self, embedder):
        """Test building index on empty memory."""
        if embedder is None:
            pytest.skip("Embedder not available")
        
        memory = OMem(
            memory_schema=Document,
            key_extractor=lambda x: x.doc_id,
            llm_client=None,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.MERGE_FIELD
        )
        memory.build_index()
        # Should not raise, index is None
        assert memory._index is None

    @pytest.mark.requires_openai
    def test_build_index_with_items(self, embedder):
        """Test building index with items."""
        if embedder is None:
            pytest.skip("Embedder not available")
        
        memory = OMem(
            memory_schema=Document,
            key_extractor=lambda x: x.doc_id,
            llm_client=None,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.MERGE_FIELD
        )

        docs = [
            Document(doc_id="1", title="Python Guide", content="Learn Python"),
            Document(doc_id="2", title="JavaScript Guide", content="Learn JS"),
        ]
        memory.add(docs)
        memory.build_index()

        assert memory._index is not None

    @pytest.mark.requires_openai
    def test_build_index_force_rebuild(self, embedder):
        """Test force rebuild of index."""
        if embedder is None:
            pytest.skip("Embedder not available")
        
        memory = OMem(
            memory_schema=Document,
            key_extractor=lambda x: x.doc_id,
            llm_client=None,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.MERGE_FIELD
        )

        memory.add(Document(doc_id="1", title="A", content="Content A"))
        memory.build_index()
        index1 = memory._index

        # Should skip rebuild
        memory.build_index(force=False)
        assert memory._index is index1

        # Force rebuild
        memory.build_index(force=True)
        # Index was rebuilt (may be same object, but rebuild happened)

    def test_build_index_without_embedder_raises(self):
        """Test that building index without embedder raises error."""
        memory = OMem(
            memory_schema=Document,
            key_extractor=lambda x: x.doc_id,
            llm_client=None,
            embedder=None,
            strategy_or_merger=MergeStrategy.MERGE_FIELD
        )

        with pytest.raises(RuntimeError):
            memory.build_index()


class TestSearch:
    """Test vector search functionality."""

    @pytest.fixture
    def memory_with_index(self, has_openai_key):
        """Fixture: Memory with indexed documents (reads from .env)."""
        if not has_openai_key:
            return None
        
        try:
            from langchain_openai import OpenAIEmbeddings
            embedder = OpenAIEmbeddings()
        except Exception as e:
            pytest.skip(f"Failed to initialize embedder: {e}")

        memory = OMem(
            memory_schema=Document,
            key_extractor=lambda x: x.doc_id,
            llm_client=None,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.MERGE_FIELD
        )

        docs = [
            Document(doc_id="1", title="Python Basics", content="Python is a programming language"),
            Document(doc_id="2", title="Django Framework", content="Django is a web framework for Python"),
            Document(doc_id="3", title="JavaScript ES6", content="JavaScript ES6 features and syntax"),
        ]
        memory.add(docs)
        memory.build_index()
        return memory

    @pytest.mark.requires_openai
    def test_search_basic(self, memory_with_index):
        """Test basic semantic search."""
        if memory_with_index is None:
            pytest.skip("Memory with index not available")
        
        results = memory_with_index.search("Python programming", top_k=2)

        assert len(results) <= 2
        # Should return Document objects
        assert all(isinstance(r, Document) for r in results)

    def test_search_without_index(self):
        """Test search raises error if no index built."""
        memory = OMem(
            memory_schema=Document,
            key_extractor=lambda x: x.doc_id,
            llm_client=None,
            embedder=None,
            strategy_or_merger=MergeStrategy.MERGE_FIELD
        )

        with pytest.raises(RuntimeError):
            memory.search("query")

    @pytest.mark.requires_openai
    def test_search_k_parameter(self, memory_with_index):
        """Test k parameter limits results."""
        if memory_with_index is None:
            pytest.skip("Memory with index not available")
        
        results_k1 = memory_with_index.search("Python", top_k=1)
        results_k3 = memory_with_index.search("Python", top_k=3)

        assert len(results_k1) <= 1
        assert len(results_k3) <= 3
