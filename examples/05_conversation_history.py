"""Conversation History Memory - Demonstrates memory evolution through dialogue.

This example simulates a conversational AI system that maintains and updates
its memory of ongoing conversations. Each turn of dialogue can add new facts,
correct previous understanding, or refine existing knowledge through intelligent
field-level merging.

Key Features:
- Conversation turn-by-turn memory updates
- Incremental fact accumulation
- Automatic conflict resolution
- Conversation context persistence
- Memory-aware response generation
"""

import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

from ontomem import OMem

# Load environment variables (OPENAI_API_KEY if available)
load_dotenv()


class ConversationMemory(BaseModel):
    """AI's evolving memory of conversation facts and context."""

    session_id: str
    user_name: str | None = None
    known_topics: list[str] = []
    user_preferences: list[str] = []
    user_interests: list[str] = []
    goals_discussed: list[str] = []
    decisions_made: list[str] = []
    open_questions: list[str] = []
    context_notes: str | None = None


def example_conversation_history():
    """Demonstrate memory building across conversation turns."""
    print("\n" + "=" * 80)
    print("CONVERSATION HISTORY MEMORY: AI Learning Through Dialogue")
    print("=" * 80)

    # Simulate TWO different conversation sessions
    all_conversation_turns = [
        # ===== SESSION 1: Career Planning (Alice) =====
        # Turn 1: Introduction
        ConversationMemory(
            session_id="conv_session_2024_001",
            user_name="Alice",
            known_topics=["career planning"],
            user_preferences=[],
            user_interests=["software development"],
            goals_discussed=["find new job opportunity"],
            decisions_made=[],
            open_questions=["What technologies are most in demand?"],
            context_notes="User is considering career transition",
        ),
        # Turn 2: Preferences emerge
        ConversationMemory(
            session_id="conv_session_2024_001",
            user_name=None,
            known_topics=["career planning", "Python", "remote work"],
            user_preferences=["remote", "flexible hours", "learning culture"],
            user_interests=["machine learning", "data science"],
            goals_discussed=["find new job opportunity", "transition to ML role"],
            decisions_made=["Will update LinkedIn profile"],
            open_questions=["What companies are hiring in ML?"],
            context_notes=None,
        ),
        # Turn 3: More specificity
        ConversationMemory(
            session_id="conv_session_2024_001",
            user_name=None,
            known_topics=["career planning", "Python", "remote work", "ML frameworks"],
            user_preferences=["remote", "flexible hours", "learning culture", "startup environment"],
            user_interests=["machine learning", "data science", "AI ethics"],
            goals_discussed=[
                "find new job opportunity",
                "transition to ML role",
                "contribute to open source",
            ],
            decisions_made=[
                "Will update LinkedIn profile",
                "Will build portfolio with ML projects",
            ],
            open_questions=["Should I pursue certifications?", "Best portfolio projects for ML?"],
            context_notes="User is technically skilled but new to ML domain",
        ),
        # Turn 4: Decision updates
        ConversationMemory(
            session_id="conv_session_2024_001",
            user_name="Alice Chen",
            known_topics=["career planning", "Python", "remote work", "ML frameworks", "interviewing"],
            user_preferences=["remote", "flexible hours", "learning culture", "startup environment", "competitive salary"],
            user_interests=["machine learning", "data science", "AI ethics", "reinforcement learning"],
            goals_discussed=[
                "find new job opportunity",
                "transition to ML role",
                "contribute to open source",
                "speak at tech conference",
            ],
            decisions_made=[
                "Will update LinkedIn profile",
                "Will build portfolio with ML projects",
                "Will study for ML interviews",
                "Will start contributing to ML open source projects",
            ],
            open_questions=["Timeline for these activities?"],
            context_notes=None,
        ),
        # ===== SESSION 2: Product Feedback (Bob) =====
        # Turn 1: Initial feedback
        ConversationMemory(
            session_id="conv_session_2024_002",
            user_name="Bob",
            known_topics=["product feedback"],
            user_preferences=[],
            user_interests=["app usability", "performance"],
            goals_discussed=["improve user experience"],
            decisions_made=[],
            open_questions=["How can I submit detailed feedback?"],
            context_notes="User is long-time customer with concerns",
        ),
        # Turn 2: Specific issues
        ConversationMemory(
            session_id="conv_session_2024_002",
            user_name=None,
            known_topics=["product feedback", "API", "mobile app"],
            user_preferences=["faster response", "better documentation"],
            user_interests=["performance optimization", "mobile-first design"],
            goals_discussed=["improve user experience", "get faster API responses"],
            decisions_made=["Will test new beta features"],
            open_questions=["When is the new mobile app launch?"],
            context_notes=None,
        ),
        # Turn 3: Detailed preferences
        ConversationMemory(
            session_id="conv_session_2024_002",
            user_name="Bob Martinez",
            known_topics=["product feedback", "API", "mobile app", "data export"],
            user_preferences=["faster response", "better documentation", "offline mode"],
            user_interests=["performance optimization", "mobile-first design", "data portability"],
            goals_discussed=[
                "improve user experience",
                "get faster API responses",
                "enable offline functionality",
            ],
            decisions_made=[
                "Will test new beta features",
                "Will participate in beta testing",
            ],
            open_questions=["Will you support data export to CSV?"],
            context_notes="User is willing to participate in beta program",
        ),
    ]

    print("\n🗣️  Conversation Progress:")
    print("-" * 80)

    for i, turn in enumerate(all_conversation_turns, 1):
        print(f"\n   Turn {i} [Session: {turn.session_id}]:")
        print(f"      Topics: {len(turn.known_topics)} | Preferences: {len(turn.user_preferences)}")
        print(f"      Goals: {len(turn.goals_discussed)} | Decisions: {len(turn.decisions_made)}")
        print(f"      Open Questions: {len(turn.open_questions)}")

    # Initialize OMem for conversation memory
    print("\n🧠 Initializing conversation memory system...")
    from ontomem.merger import MergeStrategy
    
    conversation_memory = OMem(
        memory_schema=ConversationMemory,
        key_extractor=lambda x: x.session_id,
        llm_client=None,
        embedder=None,
        merge_strategy=MergeStrategy.MERGE_FIELD,
    )

    # Add all conversation turns to memory
    print("📚 Processing conversation turns...")
    conversation_memory.add(all_conversation_turns)
    print(f"   Conversation memory consolidated into {conversation_memory.size} record(s)")

    # Retrieve consolidated memory
    print("\n📖 AI's Consolidated Memory of Conversations:")
    print("=" * 80)

    for session_id in ["conv_session_2024_001", "conv_session_2024_002"]:
        memory = conversation_memory.get(session_id)
        if memory:
            print(f"\n   📝 Session: {memory.session_id}")
            print(f"      User: {memory.user_name}")

            print(f"      👤 Known Interests: {len(memory.user_interests)} areas")
            for interest in memory.user_interests:
                print(f"         • {interest}")

            print(f"\n      🎯 Goals: {len(memory.goals_discussed)}")
            for goal in memory.goals_discussed:
                print(f"         • {goal}")

            print(f"\n      ✅ Decisions: {len(memory.decisions_made)}")
            for decision in memory.decisions_made:
                print(f"         • {decision}")

            print(f"      💼 Preferences: {', '.join(memory.user_preferences[:2]) or 'N/A'}")
            print(f"      📝 Topics: {len(memory.known_topics)} covered")

    # Memory statistics
    print("\n📊 Memory Statistics (All Sessions):")
    print("-" * 80)
    total_sessions = len(set(m.session_id for m in all_conversation_turns))
    print(f"   Total Conversations: {total_sessions}")
    print(f"   Total Memory Records: {conversation_memory.size}")
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    conversation_folder = temp_dir / "conversation_memory"

    print(f"\n💾 Saving conversation memory to {conversation_folder.relative_to(temp_dir.parent)}...")
    conversation_memory.dump(str(conversation_folder))
    print("   ✅ Memory persisted - conversation context preserved")

    # Memory statistics
    print("\n📊 Memory Statistics:")
    print("-" * 80)
    if memory:
        total_facts = (
            len(memory.known_topics)
            + len(memory.user_preferences)
            + len(memory.user_interests)
            + len(memory.goals_discussed)
            + len(memory.decisions_made)
        )
        print(f"\n   Total Facts Accumulated: {total_facts}")
        print(f"   Topics: {len(memory.known_topics)}")
        print(f"   Preferences: {len(memory.user_preferences)}")
        print(f"   Interests: {len(memory.user_interests)}")
        print(f"   Goals: {len(memory.goals_discussed)}")
        print(f"   Decisions: {len(memory.decisions_made)}")
        print(f"   Open Issues: {len(memory.open_questions)}")

    print("\n💡 Memory Evolution Insights:")
    print("-" * 80)
    print("\n   Turn by turn, the AI's understanding became:")
    print("      ✓ More specific (general → machine learning → reinforcement learning)")
    print("      ✓ More complete (preferences, interests, goals all emerged)")
    print("      ✓ More actionable (abstract goals → concrete decisions)")
    print("      ✓ More contextual (full picture of user's career trajectory)")

    print("\n" + "=" * 80)
    print("✨ AI memory evolves naturally through conversation!")
    print("=" * 80)


if __name__ == "__main__":
    example_conversation_history()
