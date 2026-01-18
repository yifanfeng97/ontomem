"""End-to-end integration tests for OntoMem."""
import pytest
from pydantic import BaseModel
from ontomem import OMem
from ontomem.merger import MergeStrategy


class BugFixKnowledge(BaseModel):
    error_signature: str
    successful_solutions: list[str] = []
    root_cause_analysis: str = ""
    avoidance_tips: str = ""


class TestSelfImprovingAgent:
    """Test the "self-improving agent" scenario from README."""

    @pytest.fixture
    def bug_memory(self):
        """Fixture: Memory for bug fixes."""
        return OMem(
            memory_schema=BugFixKnowledge,
            key_extractor=lambda x: x.error_signature,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )

    def test_agent_learns_from_repeated_errors(self, bug_memory):
        """Test agent consolidates knowledge from repeated encounters."""
        # Day 1: First ModuleNotFoundError
        bug_memory.add(BugFixKnowledge(
            error_signature="ModuleNotFoundError: No module named 'pandas'",
            successful_solutions=["Run: pip install pandas"],
            root_cause_analysis="Missing library in environment.",
            avoidance_tips="Check requirements.txt"
        ))

        # Day 2: Same error, different solution
        bug_memory.add(BugFixKnowledge(
            error_signature="ModuleNotFoundError: No module named 'pandas'",
            successful_solutions=["Run: conda install pandas"],
            root_cause_analysis="Pip failed due to binary incompatibility.",
            avoidance_tips="Prefer conda in scientific environments."
        ))

        # Verify consolidation
        knowledge = bug_memory.get("ModuleNotFoundError: No module named 'pandas'")
        assert knowledge is not None
        # Latest solution overwrites (FIELD_MERGE with exclude_none replaces list)
        assert knowledge.successful_solutions == ["Run: conda install pandas"]
        # But the analysis is updated to the latest
        assert "binary incompatibility" in knowledge.root_cause_analysis

    def test_multiple_error_types(self, bug_memory):
        """Test memory handles multiple different errors."""
        errors = [
            BugFixKnowledge(
                error_signature="ImportError: cannot import name 'X'",
                successful_solutions=["Check module structure"],
            ),
            BugFixKnowledge(
                error_signature="TypeError: 'NoneType' object is not subscriptable",
                successful_solutions=["Add None check"],
            ),
            BugFixKnowledge(
                error_signature="AttributeError: 'dict' object has no attribute 'get'",
                successful_solutions=["Use dict.get() or check type"],
            ),
        ]

        bug_memory.add(errors)
        assert bug_memory.size == 3

        # All errors should be retrievable
        for error in errors:
            retrieved = bug_memory.get(error.error_signature)
            assert retrieved is not None

    def test_memory_persistence_across_sessions(self, bug_memory, tmp_path):
        """Test memory can be saved and loaded across sessions."""
        # Session 1: Learn some bugs
        bug_memory.add([
            BugFixKnowledge(
                error_signature="ValueError: invalid literal for int()",
                successful_solutions=["Add try-except", "Validate input type"],
            ),
            BugFixKnowledge(
                error_signature="KeyError: 'key_name'",
                successful_solutions=["Use dict.get()", "Check key exists"],
            ),
        ])

        memory_dir = tmp_path / "bug_memory"
        bug_memory.dump(memory_dir)

        # Session 2: Load and verify
        bug_memory2 = OMem(
            memory_schema=BugFixKnowledge,
            key_extractor=lambda x: x.error_signature,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE
        )
        bug_memory2.load(memory_dir)

        assert bug_memory2.size == 2
        value_error = bug_memory2.get("ValueError: invalid literal for int()")
        assert value_error is not None
        assert len(value_error.successful_solutions) == 2

    def test_workflow_expand_knowledge(self, bug_memory):
        """Test realistic workflow: expand knowledge as new info arrives."""
        error_sig = "IndexError: list index out of range"

        # Initial encounter
        bug_memory.add(BugFixKnowledge(
            error_signature=error_sig,
            successful_solutions=["Check array length first"],
            root_cause_analysis="Array access without bounds check"
        ))

        # Later: More knowledge from another team member
        bug_memory.add(BugFixKnowledge(
            error_signature=error_sig,
            successful_solutions=["Use try-except-except"],
            root_cause_analysis="Off-by-one error in loop logic",
            avoidance_tips="Use enumerate instead of manual indexing"
        ))

        # Consolidated view
        knowledge = bug_memory.get(error_sig)
        # Latest solution overwrites in FIELD_MERGE mode
        assert knowledge.successful_solutions == ["Use try-except-except"]
        # But comprehensive analysis from latest update is preserved
        assert knowledge.avoidance_tips == "Use enumerate instead of manual indexing"
        assert knowledge.root_cause_analysis == "Off-by-one error in loop logic"


class TestSelfImprovingAgentWithLLM:
    """Test the "self-improving agent" scenario with LLM merging."""
    
    @pytest.fixture
    def llm_client(self, has_openai_key, llm_model):
        """Fixture: LLM client from .env."""
        if not has_openai_key:
            return None
        
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=llm_model)
        except Exception as e:
            pytest.skip(f"Failed to initialize LLM: {e}")
    
    @pytest.fixture
    def embedder(self, has_openai_key):
        """Fixture: Embedder from .env."""
        if not has_openai_key:
            return None
        
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings()
        except Exception as e:
            pytest.skip(f"Failed to initialize embedder: {e}")
    
    @pytest.mark.requires_openai
    def test_llm_driven_merge_consolidation(self, llm_client, embedder):
        """Test LLM-driven merging of bug fix knowledge."""
        if llm_client is None or embedder is None:
            pytest.skip("LLM or Embedder not available")
        
        bug_memory = OMem(
            memory_schema=BugFixKnowledge,
            key_extractor=lambda x: x.error_signature,
            llm_client=llm_client,
            embedder=embedder,
            merge_strategy=MergeStrategy.LLM.BALANCED
        )
        
        # Day 1: First ModuleNotFoundError
        bug_memory.add(BugFixKnowledge(
            error_signature="ModuleNotFoundError: No module named 'pandas'",
            successful_solutions=["Run: pip install pandas"],
            root_cause_analysis="Missing library in environment.",
            avoidance_tips="Check requirements.txt"
        ))
        
        # Day 2: Same error, different solution
        bug_memory.add(BugFixKnowledge(
            error_signature="ModuleNotFoundError: No module named 'pandas'",
            successful_solutions=["Run: conda install pandas"],
            root_cause_analysis="Pip failed due to binary incompatibility.",
            avoidance_tips="Prefer conda in scientific environments."
        ))
        
        # Verify consolidation happened
        knowledge = bug_memory.get("ModuleNotFoundError: No module named 'pandas'")
        assert knowledge is not None
        # With LLM merging, we should have synthesized solutions
        assert len(knowledge.successful_solutions) >= 1
