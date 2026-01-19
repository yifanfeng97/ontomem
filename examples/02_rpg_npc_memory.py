"""RPG NPC Memory System - Demonstrates field-level merging for character profiles.

This example simulates an RPG game where NPCs gradually build their memory of the
player character across multiple interactions. Each encounter adds new information,
and OMem intelligently merges fragments into a complete NPC perspective.

Key Features:
- Incremental profile building through field merge
- Multiple interaction types (combat, trade, dialogue)
- Progressive NPC opinion and behavior updates
"""

import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel

from ontomem import OMem


class NPCMemory(BaseModel):
    """NPC's memory record of player interactions and characteristics."""

    player_id: str
    player_name: str | None = None
    titles_earned: list[str] = []
    reputation_events: list[str] = []
    known_skills: list[str] = []
    trade_history: list[dict] = []
    first_meeting_location: str | None = None
    last_known_location: str | None = None
    npc_opinion: str | None = None
    party_relationship: str | None = None


def example_rpg_npc_memory():
    """Demonstrate NPC memory building through multiple game encounters."""
    print("\n" + "=" * 80)
    print("RPG NPC MEMORY SYSTEM: Building Character Profiles Through Play")
    print("=" * 80)

    npc_name = "Aldric the Merchant"

    # Simulate encounters with TWO different players
    all_encounter_memories = [
        # Player 1: "Theron" - Multiple encounters
        NPCMemory(
            player_id="hero_001",
            player_name="Theron",
            titles_earned=[],
            reputation_events=["Bought healing potions"],
            known_skills=[],
            trade_history=[{"item": "Healing Potion x3", "gold": 150}],
            first_meeting_location="Village Market",
            last_known_location="Village Market",
            npc_opinion=None,
            party_relationship=None,
        ),
        NPCMemory(
            player_id="hero_001",
            player_name=None,
            titles_earned=["Dragon Slayer"],
            reputation_events=["Saved village from goblin raid", "Defeated dragon"],
            known_skills=["Sword Mastery", "Magic Resistance"],
            trade_history=[{"item": "Rare Armor", "gold": 500}],
            first_meeting_location=None,
            last_known_location="Dragon Lair",
            npc_opinion="Brave warrior",
            party_relationship=None,
        ),
        NPCMemory(
            player_id="hero_001",
            player_name="Theron the Dragon Slayer",
            titles_earned=["Savior of the Realm"],
            reputation_events=["Returned lost artifact", "Defeated Dark Lord"],
            known_skills=["Ancient Magic", "Diplomacy"],
            trade_history=[{"item": "Legendary Sword", "gold": 2000}],
            first_meeting_location=None,
            last_known_location="Royal Palace",
            npc_opinion=None,
            party_relationship="Close friend",
        ),
        # Player 2: "Elena" - Different encounters
        NPCMemory(
            player_id="hero_002",
            player_name="Elena",
            titles_earned=[],
            reputation_events=["Purchased spell scrolls"],
            known_skills=["Magic"],
            trade_history=[{"item": "Fire Spell Scroll", "gold": 300}],
            first_meeting_location="Guild Hall",
            last_known_location="Guild Hall",
            npc_opinion=None,
            party_relationship=None,
        ),
        NPCMemory(
            player_id="hero_002",
            player_name="Elena the Mage",
            titles_earned=["Arcane Master"],
            reputation_events=["Defeated Dark Cult", "Saved the city from curse"],
            known_skills=["Fire Magic", "Ice Magic", "Arcane Knowledge"],
            trade_history=[{"item": "Ancient Grimoire", "gold": 1500}],
            first_meeting_location=None,
            last_known_location="Magic Tower",
            npc_opinion="Formidable mage",
            party_relationship="Respected ally",
        ),
    ]

    print(f"\n🎮 NPC: {npc_name}")
    print(f"📝 Encounters with {len({m.player_id for m in all_encounter_memories})} different players:\n")

    for i, memory in enumerate(all_encounter_memories, 1):
        print(f"  ⚔️  Encounter {i} [Player: {memory.player_id}]:")
        print(f"     Player Name: {memory.player_name or '(unknown)'}")
        print(
            f"     Titles: {', '.join(memory.titles_earned) or '(none yet)'}"
        )
        print(
            f"     Reputation Events: {len(memory.reputation_events)} events"
        )
        print(f"     Known Skills: {', '.join(memory.known_skills) or '(unknown)'}")

    # Initialize NPC memory with MERGE_FIELD strategy
    print("\n🧠 Building NPC's consolidated memory...")
    from ontomem.merger import MergeStrategy
    
    npc_memory = OMem(
        memory_schema=NPCMemory,
        key_extractor=lambda x: x.player_id,
        llm_client=None,
        embedder=None,
        strategy_or_merger=MergeStrategy.MERGE_FIELD,
    )

    # Add all encounter memories
    npc_memory.add(all_encounter_memories)
    print(f"   Memory consolidated. Storage size: {npc_memory.size}")

    # Retrieve the complete NPC memory for each player
    print("\n🔍 NPC's Complete Memory Profiles:")
    print("-" * 80)

    for player_id in ["hero_001", "hero_002"]:
        player_profile = npc_memory.get(player_id)
        if player_profile:
            print(f"\n   📖 Player ID: {player_profile.player_id}")
            print(f"      Name (Known As): {player_profile.player_name}")
            print(f"      📜 Titles Earned: {', '.join(player_profile.titles_earned) or '(none)'}")
            print(f"      🎖️  Reputation Events: {len(player_profile.reputation_events)} events")
            print(f"      ⚔️  Known Skills: {', '.join(player_profile.known_skills) or '(unknown)'}")
            print(f"      💰 Trade History: {len(player_profile.trade_history)} transactions")
            print(f"      📍 Locations: First met {player_profile.first_meeting_location}, Last seen {player_profile.last_known_location}")
            print(f"      💭 Opinion: {player_profile.npc_opinion or '(developing...)'}")
            print(f"      💞 Relationship: {player_profile.party_relationship or '(neutral)'}")

    # Persist NPC memory to file
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    npc_memory_folder = temp_dir / "npc_memory"

    print(f"\n💾 Saving NPC memory to {npc_memory_folder.relative_to(temp_dir.parent)}...")
    npc_memory.dump(str(npc_memory_folder))
    print("   ✅ NPC memory persisted")

    # Demonstrate that NPC can be questioned about player
    print("\n🗣️  NPC Dialogue System (Based on Memory):")
    print("-" * 80)
    if player_profile:
        if "Dragon Slayer" in player_profile.titles_earned:
            print(f"\n   {npc_name}: Ah, {player_profile.player_name}!")
            print("   'You are the legendary Dragon Slayer! Your deeds are sung in taverns.'")
        if player_profile.party_relationship:
            print(f"   {npc_name}: 'You've been a good friend to me and this realm.'")
        print(
            f"\n   {npc_name}: 'I remember when we first met at {player_profile.first_meeting_location}...'"
        )

    print("\n" + "=" * 80)
    print("✨ NPC's memory has evolved through gameplay!")
    print("=" * 80)


if __name__ == "__main__":
    example_rpg_npc_memory()
