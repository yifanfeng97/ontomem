"""Sample schemas for testing."""

from pydantic import BaseModel
from typing import Optional, List


class TestPerson(BaseModel):
    """Test model for person."""

    person_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    skills: List[str] = []


class TestDocument(BaseModel):
    """Test model for document."""

    doc_id: str
    title: str
    content: str
    tags: List[str] = []


class TestExperience(BaseModel):
    """Test model for experience (like debugging scenarios)."""

    exp_id: str
    scenario: str
    lessons: List[str] = []
    confidence: Optional[float] = None
