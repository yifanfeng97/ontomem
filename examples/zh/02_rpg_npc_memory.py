"""RPG NPC 记忆系统 - 演示字段级别合并在角色档案中的应用。

这个示例模拟了一个RPG游戏，其中NPC通过多次互动逐步建立对玩家角色的记忆。
每次遭遇都会添加新的信息，OMem能够智能地将片段合并为完整的NPC视角。

主要特性：
- 通过字段合并进行增量档案构建
- 多种互动类型（战斗、贸易、对话）
- 渐进式的NPC意见和行为更新
"""

import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel

from ontomem import OMem


class NPCMemory(BaseModel):
    """NPC对玩家互动和特征的记忆记录。"""

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
    """通过多个游戏遭遇演示NPC记忆构建。"""
    print("\n" + "=" * 80)
    print("RPG NPC 记忆系统：通过游戏构建角色档案")
    print("=" * 80)

    npc_name = "商人阿尔德里克"

    # 模拟与两个不同玩家的遭遇
    all_encounter_memories = [
        # 玩家1："瑟伦" - 多次遭遇
        NPCMemory(
            player_id="hero_001",
            player_name="瑟伦",
            titles_earned=[],
            reputation_events=["购买了治疗药水"],
            known_skills=[],
            trade_history=[{"item": "治疗药水 x3", "gold": 150}],
            first_meeting_location="村庄市集",
            last_known_location="村庄市集",
            npc_opinion=None,
            party_relationship=None,
        ),
        NPCMemory(
            player_id="hero_001",
            player_name=None,
            titles_earned=["屠龙者"],
            reputation_events=["拯救村庄免受地精突袭", "击败了龙"],
            known_skills=["剑术精通", "魔法抗性"],
            trade_history=[{"item": "稀有盔甲", "gold": 500}],
            first_meeting_location=None,
            last_known_location="龙巢",
            npc_opinion="勇敢的战士",
            party_relationship=None,
        ),
        NPCMemory(
            player_id="hero_001",
            player_name="瑟伦·屠龙者",
            titles_earned=["国度救星"],
            reputation_events=["归还了丢失的神器", "击败了暗黑领主"],
            known_skills=["古老魔法", "外交"],
            trade_history=[{"item": "传奇剑", "gold": 2000}],
            first_meeting_location=None,
            last_known_location="皇家宫殿",
            npc_opinion=None,
            party_relationship="亲密的朋友",
        ),
        # 玩家2："艾琳娜" - 不同的遭遇
        NPCMemory(
            player_id="hero_002",
            player_name="艾琳娜",
            titles_earned=[],
            reputation_events=["购买了法术卷轴"],
            known_skills=["魔法"],
            trade_history=[{"item": "火焰法术卷轴", "gold": 300}],
            first_meeting_location="公会大厅",
            last_known_location="公会大厅",
            npc_opinion=None,
            party_relationship=None,
        ),
        NPCMemory(
            player_id="hero_002",
            player_name="艾琳娜·法师",
            titles_earned=["秘法宗师"],
            reputation_events=["击败了暗黑邪教", "拯救了城市免受诅咒"],
            known_skills=["火焰魔法", "冰霜魔法", "秘法知识"],
            trade_history=[{"item": "古老魔法书", "gold": 1500}],
            first_meeting_location=None,
            last_known_location="魔法塔",
            npc_opinion="强大的法师",
            party_relationship="受尊敬的盟友",
        ),
    ]

    print(f"\n🎮 NPC：{npc_name}")
    print(f"📝 与{len({m.player_id for m in all_encounter_memories})}个不同玩家的遭遇：\n")

    for i, memory in enumerate(all_encounter_memories, 1):
        print(f"  ⚔️  遭遇 {i} [玩家：{memory.player_id}]：")
        print(f"     玩家名字：{memory.player_name or '（未知）'}")
        print(
            f"     获得的头衔：{', '.join(memory.titles_earned) or '（暂无）'}"
        )
        print(
            f"     声望事件：{len(memory.reputation_events)}个事件"
        )
        print(f"     已知技能：{', '.join(memory.known_skills) or '（未知）'}")

    # 使用MERGE_FIELD策略初始化NPC记忆
    print("\n🧠 构建NPC的综合记忆...")
    from ontomem.merger import MergeStrategy
    
    npc_memory = OMem(
        memory_schema=NPCMemory,
        key_extractor=lambda x: x.player_id,
        llm_client=None,
        embedder=None,
        merge_strategy=MergeStrategy.MERGE_FIELD,
    )

    # 添加所有遭遇记忆
    npc_memory.add(all_encounter_memories)
    print(f"   记忆已整合。存储大小：{npc_memory.size}")

    # 检索每个玩家的完整NPC记忆
    print("\n🔍 NPC的完整记忆档案：")
    print("-" * 80)

    for player_id in ["hero_001", "hero_002"]:
        player_profile = npc_memory.get(player_id)
        if player_profile:
            print(f"\n   📖 玩家ID：{player_profile.player_id}")
            print(f"      称呼：{player_profile.player_name}")
            print(f"      📜 获得的头衔：{', '.join(player_profile.titles_earned) or '（无）'}")
            print(f"      🎖️  声望事件：{len(player_profile.reputation_events)}个事件")
            print(f"      ⚔️  已知技能：{', '.join(player_profile.known_skills) or '（未知）'}")
            print(f"      💰 贸易历史：{len(player_profile.trade_history)}笔交易")
            print(f"      📍 地点：首次在{player_profile.first_meeting_location}见面，最后在{player_profile.last_known_location}看到")
            print(f"      💭 意见：{player_profile.npc_opinion or '（正在形成...）'}")
            print(f"      💞 关系：{player_profile.party_relationship or '（中立）'}")

    # 将NPC记忆保存到文件
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    npc_memory_folder = temp_dir / "npc_memory"

    print(f"\n💾 正在将NPC记忆保存到{npc_memory_folder.relative_to(temp_dir.parent)}...")
    npc_memory.dump(str(npc_memory_folder))
    print("   ✅ NPC记忆已保存")

    # 演示NPC可以被询问关于玩家的问题
    print("\n🗣️  NPC对话系统（基于记忆）：")
    print("-" * 80)
    if player_profile:
        if "屠龙者" in player_profile.titles_earned:
            print(f"\n   {npc_name}：啊，{player_profile.player_name}!")
            print("   '你是传奇的屠龙者！你的功绩在酒馆里被传颂。'")
        if player_profile.party_relationship:
            print(f"   {npc_name}：'你一直是我和这片领土的好朋友。'")
        print(
            f"\n   {npc_name}：'我还记得我们在{player_profile.first_meeting_location}第一次见面的时候...'"
        )

    print("\n" + "=" * 80)
    print("✨ NPC的记忆在游戏过程中不断演变！")
    print("=" * 80)


if __name__ == "__main__":
    example_rpg_npc_memory()
