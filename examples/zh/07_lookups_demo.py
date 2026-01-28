"""
示例 07: 使用 Lookups 进行多维查询
================================

本示例提供了 "Lookups"（辅助索引）功能的实际运行演示。
它展示了 OMem 如何在多维度上提供快速的 O(1) 精确匹配查询，
并在数据更新时自动维护索引的一致性。

核心概念：
1. 创建索引：为不同字段注册提取规则。
2. 自动同步：当条目发生合并（Merge）时，索引自动更新。
3. 复合键：创建复杂的键以进行特定查询。
"""

from typing import List
from pydantic import BaseModel
from ontomem import OMem, MergeStrategy

# 1. 定义数据结构
class GameEvent(BaseModel):
    """游戏世界中的结构化事件"""
    id: str           # 主键
    char_name: str    # 角色名
    location: str     # 地点
    action: str       # 动作
    timestamp: str    # 时间 (HH:MM)

def main():
    print("="*60)
    print("示例 07: OMem Lookups (辅助索引) 功能演示")
    print("="*60 + "\n")
    
    # 2. 初始化记忆
    # 我们使用 KEEP_INCOMING 策略，因此无需配置 LLM 或 Embedder，方便直接运行
    print("⚙️  正在初始化内存...")
    memory = OMem(
        memory_schema=GameEvent,
        key_extractor=lambda x: x.id,
        llm_client=None,
        embedder=None,
        strategy_or_merger=MergeStrategy.KEEP_INCOMING
    )

    # 3. 定义 Lookups (索引)
    # 这告诉 OMem："我希望能够通过这些字段瞬间找到数据"
    print("📝 正在创建 Lookups 索引...")
    memory.create_lookup("by_character", lambda x: x.char_name)
    memory.create_lookup("by_location", lambda x: x.location)
    
    # ---------------------------------------------------------
    # 场景 1: 基础写入与查询
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("场景 1: 基础写入与查询")
    print("-" * 40)
    
    events = [
        GameEvent(id="e1", char_name="亚拉贡", location="瑞文戴尔", action="制定计划", timestamp="08:00"),
        GameEvent(id="e2", char_name="亚拉贡", location="荒野", action="追踪痕迹", timestamp="14:00"),
        GameEvent(id="e3", char_name="弗罗多", location="瑞文戴尔", action="休息", timestamp="09:00"),
        GameEvent(id="e4", char_name="甘道夫", location="夏尔", action="吸烟斗", timestamp="10:00"),
    ]
    memory.add(events)
    print(f"✅ 已添加 {len(events)} 条事件到内存中。\n")

    # 按角色查询
    target_char = "亚拉贡"
    results = memory.get_by_lookup("by_character", target_char)
    print(f"🔍 查询 'by_character'='{target_char}': 找到 {len(results)} 条事件")
    for e in results:
        print(f"   -> [{e.timestamp}] 在 {e.location} {e.action}")

    # 按地点查询
    target_loc = "瑞文戴尔"
    results = memory.get_by_lookup("by_location", target_loc)
    print(f"\n🔍 查询 'by_location'='{target_loc}': 找到 {len(results)} 条事件")
    for e in results:
        print(f"   -> [{e.timestamp}] {e.char_name}: {e.action}")

    # ---------------------------------------------------------
    # 场景 2: 数据更新时的一致性 (Merge)
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("场景 2: 自动一致性检查")
    print("-" * 40)
    print("正在模拟通过 Merge 进行属性更新...")
    
    # 检查弗罗多的当前状态
    frodo_event = memory.get("e3")
    print(f"1. 更新前: 弗罗多位于 '{frodo_event.location}'")
    
    # 更新: 弗罗多移动到了 "摩瑞亚"
    # 相同的 ID 'e3' 会触发合并操作。地点从 瑞文戴尔 -> 摩瑞亚
    update_event = GameEvent(id="e3", char_name="弗罗多", location="摩瑞亚", action="奔跑", timestamp="18:00")
    memory.add(update_event)
    print("   (更新已应用: 地点变更为 '摩瑞亚')")

    # 验证 Lookups 是否自动更新
    # 1. 应该不再出现在 '瑞文戴尔' 索引中
    old_loc_res = memory.get_by_lookup("by_location", "瑞文戴尔")
    # 2. 应该现在出现在 '摩瑞亚' 索引中
    new_loc_res = memory.get_by_lookup("by_location", "摩瑞亚")
    
    print("\n2. 验证合并后的索引状态:")
    print(f"   查询 '瑞文戴尔': 找到 {len(old_loc_res)} 条 (预期: 1, 只有亚拉贡)")
    print(f"   查询 '摩瑞亚':   找到 {len(new_loc_res)} 条 (预期: 1, 弗罗多)")
    
    if len(new_loc_res) == 1 and new_loc_res[0].char_name == "弗罗多":
        print("✅ 成功: 索引已自动同步！")
    else:
        print("❌ 失败: 索引一致性出现问题。")

    # ---------------------------------------------------------
    # 场景 3: 复杂/复合键
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("场景 3: 高级复合键查询")
    print("-" * 40)
    # 创建一个结合了 时间(小时) + 地点 的索引
    # 例如: "08:瑞文戴尔"
    print("正在创建复合索引 'time_loc' (小时:地点)...")
    memory.create_lookup(
        "time_loc", 
        lambda x: f"{x.timestamp.split(':')[0]}:{x.location}"
    )
    
    search_key = "08:瑞文戴尔"
    results = memory.get_by_lookup("time_loc", search_key)
    print(f"🔍 复合查询 '{search_key}': 找到 {len(results)} 条事件")
    if results:
        print(f"   -> {results[0].char_name} 正在 {results[0].action}")


if __name__ == "__main__":
    main()
