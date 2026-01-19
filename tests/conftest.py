"""Shared pytest configuration and fixtures."""
import pytest
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel


# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Read configuration values
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_LLM_MODEL = "gpt-4o-mini"


@pytest.fixture(scope="session")
def has_openai_key():
    """Check if OpenAI API key is available from .env."""
    return bool(OPENAI_API_KEY)


@pytest.fixture(scope="session")
def llm_model():
    """Get the default LLM model."""
    return DEFAULT_LLM_MODEL


@pytest.fixture
def openai_api_key():
    """Fixture: OpenAI API key from .env."""
    if not OPENAI_API_KEY:
        pytest.skip("OPENAI_API_KEY not found in .env")
    return OPENAI_API_KEY


@pytest.fixture
def simple_model():
    """Fixture: Simple test model."""
    class SimpleItem(BaseModel):
        item_id: str
        name: str | None = None
        value: int = 0

    return SimpleItem


# Mark tests that require OpenAI
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_openai: mark test as requiring OpenAI API key from .env"
    )
    
    # 在启动时打印信息
    if OPENAI_API_KEY:
        print("\n[OK] OpenAI API key found. LLM tests enabled.")
        print(f"   Model: {DEFAULT_LLM_MODEL}")
    else:
        print("\n[WARN]  OpenAI API key NOT found in .env. LLM tests will be skipped.")


@pytest.fixture(autouse=True)
def skip_if_no_openai(request, has_openai_key):
    """Auto-skip tests marked with requires_openai if key unavailable."""
    if request.node.get_closest_marker("requires_openai"):
        if not has_openai_key:
            pytest.skip("OPENAI_API_KEY not available in .env")
