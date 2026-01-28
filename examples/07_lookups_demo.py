"""
Example 07: Multi-dimensional Queries with Lookups
==================================================

This example provides a RUNNABLE demonstration of the 'Lookups' feature (Secondary Indices).
It shows how OMem maintains O(1) fast, exact-match queries across multiple dimensions
and automatically handles data consistency when items are updated.

Key Concepts:
1. Creating Index: Registering extraction rules for different fields.
2. Automatic Sync: Indices update automatically when items are merged.
3. Composite Keys: Creating complex keys for specialized queries.
"""

from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from ontomem import OMem, MergeStrategy

# Load environment variables (OPENAI_API_KEY if available)
load_dotenv()

# 1. Define Schema
class GameEvent(BaseModel):
    """A structured event in a game world."""
    id: str           # Primary Key
    char_name: str    # Character name
    location: str     # Where it happened
    action: str       # What happened
    timestamp: str    # Time (HH:MM)

def main():
    print("="*60)
    print("Example 07: OMem Lookups (Secondary Indices) Demo")
    print("="*60 + "\n")
    
    # 2. Initialize Memory
    # We use KEEP_INCOMING strategy so we don't need an LLM or Embedder for this demo
    print("⚙️  Initializing Memory...")
    memory = OMem(
        memory_schema=GameEvent,
        key_extractor=lambda x: x.id,
        llm_client=None,
        embedder=None,
        strategy_or_merger=MergeStrategy.KEEP_INCOMING
    )

    # 3. Define Lookups (Indices)
    # This tells OMem: "I want to be able to find items by these fields instantly"
    print("📝 Creating Lookups/Indices...")
    memory.create_lookup("by_character", lambda x: x.char_name)
    memory.create_lookup("by_location", lambda x: x.location)
    
    # ---------------------------------------------------------
    # Scenario 1: Basic Ingestion and Querying
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("Scenario 1: Basic Ingestion & Querying")
    print("-" * 40)
    
    events = [
        GameEvent(id="e1", char_name="Aragorn", location="Rivendell", action="Planning", timestamp="08:00"),
        GameEvent(id="e2", char_name="Aragorn", location="Wilderness", action="Tracking", timestamp="14:00"),
        GameEvent(id="e3", char_name="Frodo", location="Rivendell", action="Resting", timestamp="09:00"),
        GameEvent(id="e4", char_name="Gandalf", location="Shire", action="Smoking", timestamp="10:00"),
    ]
    memory.add(events)
    print(f"✅ Added {len(events)} events to memory.\n")

    # Query by Character
    target_char = "Aragorn"
    results = memory.get_by_lookup("by_character", target_char)
    print(f"🔍 Query 'by_character'='{target_char}': Found {len(results)} events")
    for e in results:
        print(f"   -> [{e.timestamp}] {e.action} at {e.location}")

    # Query by Location
    target_loc = "Rivendell"
    results = memory.get_by_lookup("by_location", target_loc)
    print(f"\n🔍 Query 'by_location'='{target_loc}': Found {len(results)} events")
    for e in results:
        print(f"   -> [{e.timestamp}] {e.char_name}: {e.action}")

    # ---------------------------------------------------------
    # Scenario 2: Data Consistency during Updates (Merge)
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("Scenario 2: Automatic Consistency Check")
    print("-" * 40)
    print("Simulating an attribute update via Merge...")
    
    # Check Frodo's current state
    frodo_event = memory.get("e3")
    print(f"1. Before Update: Frodo is at '{frodo_event.location}'")
    
    # Update: Frodo moves to 'Moria'
    # Same ID 'e3' triggers a merge operation. Location changes from Rivendell -> Moria
    update_event = GameEvent(id="e3", char_name="Frodo", location="Moria", action="Running", timestamp="18:00")
    memory.add(update_event)
    print("   (Update Applied: Location changed to 'Moria')")

    # Verify Lookups updated automatically
    # 1. Should NO LONGER replace in the 'Rivendell' index
    old_loc_res = memory.get_by_lookup("by_location", "Rivendell")
    # 2. Should NOW appear in the 'Moria' index
    new_loc_res = memory.get_by_lookup("by_location", "Moria")
    
    print("\n2. Verifying Indices post-merge:")
    print(f"   Query 'Rivendell': Found {len(old_loc_res)} (Expected: 1, Aragorn only)")
    print(f"   Query 'Moria':     Found {len(new_loc_res)} (Expected: 1, Frodo)")
    
    if len(new_loc_res) == 1 and new_loc_res[0].char_name == "Frodo":
        print("✅ SUCCESS: Index automatically synchronized!")
    else:
        print("❌ FAILED: Index consistency issue.")

    # ---------------------------------------------------------
    # Scenario 3: Complex/Composite Keys
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("Scenario 3: Advanced Composite Keys")
    print("-" * 40)
    # Create an index combining Time hour + Location
    # E.g., "08:Rivendell"
    print("Creating composite index 'time_loc' (Hour:Location)...")
    memory.create_lookup(
        "time_loc", 
        lambda x: f"{x.timestamp.split(':')[0]}:{x.location}"
    )
    
    search_key = "08:Rivendell"
    results = memory.get_by_lookup("time_loc", search_key)
    print(f"🔍 Composite Query '{search_key}': Found {len(results)} event(s)")
    if results:
        print(f"   -> {results[0].char_name} was {results[0].action}")


if __name__ == "__main__":
    main()
