"""
示例 06：时序记忆整合 (时间切片聚合)

本示例展示 OntoMem 如何高效处理时序数据。
通过使用复合键 (日期 + 用户ID)，OntoMem 自动将同一天内的碎片化观察
合并为单一的"每日摘要"记录，同时保持不同日期的记录相互独立。

这对于流数据处理异常强大：将数千条碎片化日志转化为结构化的、由 LLM 
综合生成的每日记录，无需任何手动操作。
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
    print("⚠️  请安装: pip install langchain-openai ontomem")
    exit(1)


# 加载环境变量（如果可用则加载OPENAI_API_KEY）
load_dotenv()

# 1. 定义"每日用户轨迹"的模式
class DailyUserTrace(BaseModel):
    """
    用户特定日期的活动整合记忆。
    我们不存储数千条原始日志，而是每天存储一个结构化对象。
    """
    user_id: str
    date_str: str = Field(description="YYYY-MM-DD 格式")
    
    # 我们希望在一天中不断合并这些列表
    visited_pages: List[str] = Field(default_factory=list)
    actions_performed: List[str] = Field(default_factory=list)
    
    # 我们希望 LLM 将这些综合成情绪摘要
    mood_observations: List[str] = Field(default_factory=list)
    daily_summary: Optional[str] = Field(
        default=None, 
        description="LLM 综合生成的当日行为摘要"
    )


def example_temporal_consolidation():
    print("\n" + "="*70)
    print("✨ 示例 06: 时序记忆 (时间切片聚合)")
    print("="*70)

    # 清理旧数据
    memory_folder = "temp/temporal_memory"
    if os.path.exists(memory_folder):
        shutil.rmtree(memory_folder)

    # 2. 初始化 OMem 并使用复合键
    # 核心魔法在这里：key = f"{user_id}_{date}"
    # 这意味着用户 Alice 在 2024-01-01 的所有数据会合并到一个对象中。
    # 而她在 2024-01-02 的数据会成为一个新的对象。
    print("\n📊 初始化记忆库，使用复合键: (user_id, date)")
    print("   → 同一天的所有事件自动合并为一条记录")
    
    memory = OMem(
        memory_schema=DailyUserTrace,
        key_extractor=lambda x: f"{x.user_id}_{x.date_str}",  # <--- 复合键
        llm_client=ChatOpenAI(model="gpt-4o"),
        embedder=OpenAIEmbeddings(),
        strategy_or_merger=MergeStrategy.LLM.BALANCED
    )

    print("\n" + "-"*70)
    print("📅 第 1 天：2024-01-01 (流式碎片事件)")
    print("-"*70)
    
    # 想象这些事件是一整天内陆续到来的流数据
    events_day1 = [
        DailyUserTrace(
            user_id="alice", date_str="2024-01-01",
            visited_pages=["/home", "/login"],
            actions_performed=["login_success"],
            mood_observations=["用户看起来很专注，快速登录"]
        ),
        DailyUserTrace(
            user_id="alice", date_str="2024-01-01",
            visited_pages=["/products/shoes"],
            mood_observations=["随意浏览中"]
        ),
        DailyUserTrace(
            user_id="alice", date_str="2024-01-01",
            actions_performed=["add_to_cart", "checkout"],
            mood_observations=["很兴奋，快速完成了购买"]
        )
    ]

    print(f"\n📥 为 Alice 流式写入 1月1日 的 {len(events_day1)} 个碎片事件...\n")
    for i, event in enumerate(events_day1, 1):
        print(f"   [{i}] 页面: {event.visited_pages}, 动作: {event.actions_performed}")
        memory.add(event)

    print("\n" + "-"*70)
    print("📅 第 2 天：2024-01-02 (新上下文 → 新记录)")
    print("-"*70)
    
    # 第二天 - 应该是一条独立的记录 (不同的复合键！)
    event_day2 = DailyUserTrace(
        user_id="alice", date_str="2024-01-02",
        visited_pages=["/support", "/returns"],
        mood_observations=["用户看起来很沮丧，正在寻找退款按钮"]
    )
    print("\n📥 为 Alice 写入 1月2日 的事件 (售后问题)...\n")
    print(f"   页面: {event_day2.visited_pages}")
    memory.add(event_day2)

    # 3. 检索并展示结果
    print("\n" + "="*70)
    print("🧠 记忆状态分析")
    print("="*70)
    
    # 检查第 1 天
    day1_record = memory.get("alice_2024-01-01")
    print(f"\n[记录 1] Alice 在 2024-01-01:")
    print(f"  复合键: 'alice_2024-01-01'")
    print(f"  访问过的页面 (已合并): {day1_record.visited_pages}")
    print(f"  执行的动作 (已合并): {day1_record.actions_performed}")
    print(f"  LLM 每日摘要:")
    print(f"    >>> {day1_record.daily_summary}")

    # 检查第 2 天
    day2_record = memory.get("alice_2024-01-02")
    print(f"\n[记录 2] Alice 在 2024-01-02:")
    print(f"  复合键: 'alice_2024-01-02'")
    print(f"  访问过的页面: {day2_record.visited_pages}")
    print(f"  LLM 每日摘要:")
    print(f"    >>> {day2_record.daily_summary}")

    # 4. 跨时间搜索
    print("\n" + "="*70)
    print("🔍 跨时间语义搜索")
    print("="*70)
    query = "用户什么时候感到沮丧或遇到问题了？"
    print(f"\n查询: '{query}'")
    results = memory.search(query, top_k=1)
    
    if results:
        for trace in results:
            print(f"\n  📍 找到日期: {trace.date_str}")
            print(f"  📝 摘要: {trace.daily_summary}")

    # 5. 保存
    memory.dump(memory_folder)
    print(f"\n✅ 时序记忆已保存至 {memory_folder}")
    print("\n" + "="*70)
    print("💡 核心启示:")
    print("   只改变一行代码 (key_extractor)，我们就从")
    print("   '存储数千条原始事件' 变成了 '存储 N 条整合的每日记录'")
    print("="*70 + "\n")


if __name__ == "__main__":
    example_temporal_consolidation()
