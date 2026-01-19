"""Self-Improving Debugger - Demonstrates LLM-powered merge strategy.

This example shows how OMem uses LLM.BALANCED merge to consolidate multiple
error encounters into unified, actionable solutions. Each time the debugger
encounters an error, it learns from previous experiences and generates better
solutions through intelligent merging.

Key Features:
- LLM-based merge strategy for intelligent consolidation
- Error deduplication and solution refinement
- Learning across multiple debugging sessions
"""

import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

from ontomem import OMem

# Load environment variables (OPENAI_API_KEY if available)
load_dotenv()


class DebugLog(BaseModel):
    """Debug log entry with error context and solutions."""

    error_id: str
    error_type: str
    error_message: str
    stack_trace: str | None = None
    solutions: list[str] = []
    attempted_fixes: list[str] = []
    root_cause: str | None = None


def example_self_improving_debugger():
    """Demonstrate LLM-powered debugging with intelligent error consolidation."""
    print("\n" + "=" * 80)
    print("SELF-IMPROVING DEBUGGER: LLM-Powered Error Consolidation")
    print("=" * 80)

    # Simulate multiple errors (2 different error types)
    all_debug_logs = [
        # Error Type 1: ModuleNotFoundError - encountered multiple times
        DebugLog(
            error_id="ERR_MODULE_NOT_FOUND",
            error_type="ModuleNotFoundError",
            error_message="No module named 'numpy'",
            stack_trace="File app.py, line 5 in <module>\n    import numpy as np",
            solutions=["Install numpy: pip install numpy"],
            attempted_fixes=[],
            root_cause=None,
        ),
        DebugLog(
            error_id="ERR_MODULE_NOT_FOUND",
            error_type="ModuleNotFoundError",
            error_message="No module named 'numpy'",
            stack_trace="File utils.py, line 42 in calculate\n    result = np.array(data)",
            solutions=[
                "Install numpy: pip install numpy",
                "Add numpy to requirements.txt",
            ],
            attempted_fixes=["Ran pip install numpy"],
            root_cause="Dependency not installed",
        ),
        DebugLog(
            error_id="ERR_MODULE_NOT_FOUND",
            error_type="ModuleNotFoundError",
            error_message="No module named 'numpy'",
            stack_trace="File vectorize.py, line 8 in process\n    import numpy",
            solutions=[
                "Install numpy",
                "Check virtual environment activation",
                "Update pip: pip install --upgrade pip",
            ],
            attempted_fixes=[
                "Ran pip install numpy",
                "Checked venv activation",
            ],
            root_cause="Dependency missing from venv",
        ),
        # Error Type 2: AttributeError - different error encountered multiple times
        DebugLog(
            error_id="ERR_ATTRIBUTE_ERROR",
            error_type="AttributeError",
            error_message="'NoneType' object has no attribute 'split'",
            stack_trace="File processor.py, line 23 in process\n    parts = text.split()",
            solutions=["Check if text is None before calling split()"],
            attempted_fixes=[],
            root_cause=None,
        ),
        DebugLog(
            error_id="ERR_ATTRIBUTE_ERROR",
            error_type="AttributeError",
            error_message="'NoneType' object has no attribute 'split'",
            stack_trace="File parser.py, line 15 in parse\n    tokens = data.split(',')",
            solutions=[
                "Add None check before split()",
                "Use getattr with default value",
            ],
            attempted_fixes=["Added if data is not None check"],
            root_cause="Returned None from upstream function",
        ),
    ]

    print("\n📋 Error Encounters Log:")
    for i, encounter in enumerate(all_debug_logs, 1):
        print(f"\n  Encounter {i} [{encounter.error_id}]:")
        print(f"    Error: {encounter.error_message}")
        print(f"    Solutions proposed: {len(encounter.solutions)}")
        print(f"    Attempted fixes: {len(encounter.attempted_fixes)}")

    # Initialize OMem with LLM-based merge (if API key available)
    print("\n🤖 Initializing debugger memory with intelligent merging...")

    from ontomem.merger import MergeStrategy
    
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o-mini")
        print("   ✅ OpenAI API key found - using LLM-based merging")

        omem = OMem(
            memory_schema=DebugLog,
            key_extractor=lambda x: x.error_id,
            llm_client=llm,
            embedder=None,
            merge_strategy=MergeStrategy.LLM.BALANCED,
        )
    except Exception as e:
        print(f"   ⚠️  LLM not available ({type(e).__name__}) - using field merge instead")
        omem = OMem(
            memory_schema=DebugLog,
            key_extractor=lambda x: x.error_id,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.MERGE_FIELD,
        )

    # Add all encounters to memory
    print("\n📚 Adding error encounters to memory...")
    omem.add(all_debug_logs)
    print(f"   Memory size: {omem.size}")

    # Retrieve consolidated debug logs for each error type
    print("\n🔍 Consolidated Debug Logs (After Intelligent Merging):")
    for error_id in ["ERR_MODULE_NOT_FOUND", "ERR_ATTRIBUTE_ERROR"]:
        consolidated = omem.get(error_id)
        if consolidated:
            print(f"\n   Error ID: {consolidated.error_id}")
            print(f"   Error Type: {consolidated.error_type}")
            print(f"   Error Message: {consolidated.error_message}")
            print(f"   Root Cause: {consolidated.root_cause or 'Inferred from multiple encounters'}")
            print(f"\n   📌 All Solutions Found:")
            for j, solution in enumerate(consolidated.solutions, 1):
                print(f"      {j}. {solution}")
            print(f"\n   ✓ Attempted Fixes:")
            for j, fix in enumerate(consolidated.attempted_fixes, 1):
                print(f"      {j}. {fix}")

    # Persist to temp directory
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    memory_folder = temp_dir / "debugger_memory"

    print(f"\n💾 Persisting debugger memory to {memory_folder.relative_to(temp_dir.parent)}...")
    omem.dump(str(memory_folder))
    print("   ✅ Memory persisted")

    # Demonstrate loading previous memory
    print("\n📖 Loading previous debugger memory...")
    from ontomem.merger import MergeStrategy
    
    omem_restored = OMem(
        memory_schema=DebugLog,
        key_extractor=lambda x: x.error_id,
        llm_client=None,
        embedder=None,
        merge_strategy=MergeStrategy.MERGE_FIELD,
    )
    omem_restored.load(str(memory_folder))
    print(f"   ✅ Restored memory size: {omem_restored.size}")

    # Show memory contents for each error type
    print("\n📚 Restored Error Database:")
    for error_id in ["ERR_MODULE_NOT_FOUND", "ERR_ATTRIBUTE_ERROR"]:
        restored_log = omem_restored.get(error_id)
        if restored_log:
            print(f"\n   [{error_id}]")
            print(f"      Error type: {restored_log.error_type}")
            print(f"      Solutions count: {len(restored_log.solutions)}")

    print("\n" + "=" * 80)
    print("✨ Debugger learned from multiple encounters!")
    print("=" * 80)


if __name__ == "__main__":
    example_self_improving_debugger()
