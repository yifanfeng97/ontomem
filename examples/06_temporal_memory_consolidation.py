"""
Example 06: Temporal Memory Consolidation (Time-Slicing)

This example demonstrates how OntoMem effectively handles time-series data.
By using a composite key (date + user_id), OntoMem automatically consolidates
fragmented observations from the same day into a single "Daily Summary" record,
while keeping different days separate.

This is incredibly powerful for stream processing: turn 1000s of fragmented logs
into structured, LLM-synthesized daily records with zero manual effort.
"""

import os
import shutil
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ontomem import OMem, MergeStrategy
except ImportError:
    print("⚠️  Please install: pip install langchain-openai ontomem")
    exit(1)

# Load environment variables (OPENAI_API_KEY if available)
load_dotenv()

# 1. Define a schema for a "Daily User Trace"
class DailyUserTrace(BaseModel):
    """
    Consolidated memory of a user's activity for a specific day.
    Instead of storing 1000s of raw logs, we store one structured object per day.
    """
    user_id: str
    date_str: str = Field(description="YYYY-MM-DD format")
    
    # We want to merge these lists throughout the day
    visited_pages: List[str] = Field(default_factory=list)
    actions_performed: List[str] = Field(default_factory=list)
    
    # We want the LLM to synthesize these into a mood summary
    mood_observations: List[str] = Field(default_factory=list)
    daily_summary: Optional[str] = Field(
        default=None, 
        description="LLM synthesized summary of the day's behavior"
    )


def example_temporal_consolidation():
    print("\n" + "="*70)
    print("✨ Example 06: Temporal Memory (Time-Slicing Consolidation)")
    print("="*70)

    # Clean up previous run
    memory_folder = "temp/temporal_memory"
    if os.path.exists(memory_folder):
        shutil.rmtree(memory_folder)

    # 2. Initialize OMem with a COMPOSITE KEY
    # The magic happens here: key = f"{user_id}_{date}"
    # This means all data for User A on 2024-01-01 merges into ONE object.
    # Data for User A on 2024-01-02 becomes a NEW object.
    print("\n📊 Initializing Memory with Composite Key: (user_id, date)")
    print("   → All events from same day auto-merge into one record")
    
    memory = OMem(
        memory_schema=DailyUserTrace,
        key_extractor=lambda x: f"{x.user_id}_{x.date_str}",  # <--- Composite Key
        llm_client=ChatOpenAI(model="gpt-4o"),
        embedder=OpenAIEmbeddings(),
        strategy_or_merger=MergeStrategy.LLM.BALANCED
    )

    print("\n" + "-"*70)
    print("📅 DAY 1: 2024-01-01 (Streaming Fragmented Events)")
    print("-"*70)
    
    # Imagine these events come in as a stream throughout the day
    events_day1 = [
        DailyUserTrace(
            user_id="alice", date_str="2024-01-01",
            visited_pages=["/home", "/login"],
            actions_performed=["login_success"],
            mood_observations=["User seems focused, logged in quickly"]
        ),
        DailyUserTrace(
            user_id="alice", date_str="2024-01-01",
            visited_pages=["/products/shoes"],
            mood_observations=["Browsing casually"]
        ),
        DailyUserTrace(
            user_id="alice", date_str="2024-01-01",
            actions_performed=["add_to_cart", "checkout"],
            mood_observations=["Excited, completed purchase fast"]
        )
    ]

    print(f"\n📥 Streaming {len(events_day1)} fragmented events for Alice on Jan 1st...\n")
    for i, event in enumerate(events_day1, 1):
        print(f"   [{i}] Pages: {event.visited_pages}, Actions: {event.actions_performed}")
        memory.add(event)

    print("\n" + "-"*70)
    print("📅 DAY 2: 2024-01-02 (New Context → New Record)")
    print("-"*70)
    
    # Next day - should be a separate record (different composite key!)
    event_day2 = DailyUserTrace(
        user_id="alice", date_str="2024-01-02",
        visited_pages=["/support", "/returns"],
        mood_observations=["User seems frustrated, looking for refund button"]
    )
    print("\n📥 Streaming event for Alice on Jan 2nd (Support issue)...\n")
    print(f"   Pages: {event_day2.visited_pages}")
    memory.add(event_day2)

    # 3. Retrieve and Show Results
    print("\n" + "="*70)
    print("🧠 MEMORY STATE ANALYSIS")
    print("="*70)
    
    # Check Day 1
    day1_record = memory.get("alice_2024-01-01")
    print(f"\n[Record 1] Alice on 2024-01-01:")
    print(f"  Composite Key: 'alice_2024-01-01'")
    print(f"  Pages Visited (Merged): {day1_record.visited_pages}")
    print(f"  Actions (Merged): {day1_record.actions_performed}")
    print(f"  LLM Daily Summary:")
    print(f"    >>> {day1_record.daily_summary}")

    # Check Day 2
    day2_record = memory.get("alice_2024-01-02")
    print(f"\n[Record 2] Alice on 2024-01-02:")
    print(f"  Composite Key: 'alice_2024-01-02'")
    print(f"  Pages Visited: {day2_record.visited_pages}")
    print(f"  LLM Daily Summary:")
    print(f"    >>> {day2_record.daily_summary}")

    # 4. Search across time
    print("\n" + "="*70)
    print("🔍 SEMANTIC SEARCH ACROSS TIME")
    print("="*70)
    query = "When was the user feeling frustrated or having issues?"
    print(f"\nQuery: '{query}'")
    results = memory.search(query, top_k=1)
    
    if results:
        for trace in results:
            print(f"\n  📍 Found on: {trace.date_str}")
            print(f"  📝 Summary: {trace.daily_summary}")

    # 5. Save
    memory.dump(memory_folder)
    print(f"\n✅ Temporal memories saved to {memory_folder}")
    print("\n" + "="*70)
    print("💡 Key Takeaway:")
    print("   By changing ONE line (key_extractor), we transformed from")
    print("   'Store 1000s of raw events' to 'Store N consolidated daily records'")
    print("="*70 + "\n")


if __name__ == "__main__":
    example_temporal_consolidation()
