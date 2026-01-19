"""对话历史记忆 - 演示通过对话进行的记忆演变。

此示例模拟了一个会话式AI系统，该系统维持和更新
对于正在进行的对话的记忆。每个对话回合都可以添加
新事实、纠正以前的理解或通过智能字段级别合并来完善现有知识。

主要特性：
- 对话逐轮的记忆更新
- 增量事实积累
- 自动冲突解决
- 对话上下文持久化
- 记忆感知响应生成
"""

import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

from ontomem import OMem

# 加载环境变量（如果可用则加载OPENAI_API_KEY）
load_dotenv()


class ConversationMemory(BaseModel):
    """AI对对话事实和上下文的不断演变的记忆。"""

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
    """演示在对话回合中的记忆构建。"""
    print("\n" + "=" * 80)
    print("对话历史记忆：AI通过对话学习")
    print("=" * 80)

    # 模拟两个不同的对话会话
    all_conversation_turns = [
        # ===== 会话1：职业规划（爱丽丝）=====
        # 第1回合：介绍
        ConversationMemory(
            session_id="conv_session_2024_001",
            user_name="爱丽丝",
            known_topics=["职业规划"],
            user_preferences=[],
            user_interests=["软件开发"],
            goals_discussed=["寻找新的工作机会"],
            decisions_made=[],
            open_questions=["哪些技术最受欢迎？"],
            context_notes="用户正在考虑职业转变",
        ),
        # 第2回合：出现偏好
        ConversationMemory(
            session_id="conv_session_2024_001",
            user_name=None,
            known_topics=["职业规划", "Python", "远程工作"],
            user_preferences=["远程", "灵活的工作时间", "学习文化"],
            user_interests=["机器学习", "数据科学"],
            goals_discussed=["寻找新的工作机会", "过渡到机器学习角色"],
            decisions_made=["将更新LinkedIn档案"],
            open_questions=["哪些公司在招聘机器学习岗位？"],
            context_notes=None,
        ),
        # 第3回合：更多具体性
        ConversationMemory(
            session_id="conv_session_2024_001",
            user_name=None,
            known_topics=["职业规划", "Python", "远程工作", "机器学习框架"],
            user_preferences=["远程", "灵活的工作时间", "学习文化", "初创公司环境"],
            user_interests=["机器学习", "数据科学", "人工智能伦理"],
            goals_discussed=[
                "寻找新的工作机会",
                "过渡到机器学习角色",
                "贡献开源项目",
            ],
            decisions_made=[
                "将更新LinkedIn档案",
                "将使用机器学习项目构建作品集",
            ],
            open_questions=["我应该追求认证吗？", "机器学习最好的作品集项目是什么？"],
            context_notes="用户在技术上有技能，但在机器学习领域是新手",
        ),
        # 第4回合：决策更新
        ConversationMemory(
            session_id="conv_session_2024_001",
            user_name="爱丽丝·陈",
            known_topics=["职业规划", "Python", "远程工作", "机器学习框架", "面试"],
            user_preferences=["远程", "灵活的工作时间", "学习文化", "初创公司环境", "有竞争力的薪水"],
            user_interests=["机器学习", "数据科学", "人工智能伦理", "强化学习"],
            goals_discussed=[
                "寻找新的工作机会",
                "过渡到机器学习角色",
                "贡献开源项目",
                "在技术会议上发言",
            ],
            decisions_made=[
                "将更新LinkedIn档案",
                "将使用机器学习项目构建作品集",
                "将为机器学习面试做准备",
                "将开始为机器学习开源项目做贡献",
            ],
            open_questions=["这些活动的时间表是什么？"],
            context_notes=None,
        ),
        # ===== 会话2：产品反馈（鲍勃）=====
        # 第1回合：初步反馈
        ConversationMemory(
            session_id="conv_session_2024_002",
            user_name="鲍勃",
            known_topics=["产品反馈"],
            user_preferences=[],
            user_interests=["应用易用性", "性能"],
            goals_discussed=["改进用户体验"],
            decisions_made=[],
            open_questions=["我如何提交详细反馈？"],
            context_notes="长期客户有些担忧",
        ),
        # 第2回合：具体问题
        ConversationMemory(
            session_id="conv_session_2024_002",
            user_name=None,
            known_topics=["产品反馈", "API", "移动应用"],
            user_preferences=["更快的响应", "更好的文档"],
            user_interests=["性能优化", "移动优先设计"],
            goals_discussed=["改进用户体验", "获得更快的API响应"],
            decisions_made=["将测试新的测试版功能"],
            open_questions=["新的移动应用何时发布？"],
            context_notes=None,
        ),
        # 第3回合：详细偏好
        ConversationMemory(
            session_id="conv_session_2024_002",
            user_name="鲍勃·马丁内斯",
            known_topics=["产品反馈", "API", "移动应用", "数据导出"],
            user_preferences=["更快的响应", "更好的文档", "离线模式"],
            user_interests=["性能优化", "移动优先设计", "数据可携带性"],
            goals_discussed=[
                "改进用户体验",
                "获得更快的API响应",
                "启用离线功能",
            ],
            decisions_made=[
                "将测试新的测试版功能",
                "将参加测试版测试",
            ],
            open_questions=["你会支持导出数据到CSV吗？"],
            context_notes="用户愿意参加测试版计划",
        ),
    ]

    print("\n🗣️  对话进展：")
    print("-" * 80)

    for i, turn in enumerate(all_conversation_turns, 1):
        print(f"\n   回合 {i}【会话：{turn.session_id}】：")
        print(f"      主题：{len(turn.known_topics)}个 | 偏好：{len(turn.user_preferences)}个")
        print(f"      目标：{len(turn.goals_discussed)}个 | 决策：{len(turn.decisions_made)}个")
        print(f"      开放问题：{len(turn.open_questions)}个")

    # 初始化OMem进行对话记忆
    print("\n🧠 初始化对话记忆系统...")
    from ontomem.merger import MergeStrategy
    
    conversation_memory = OMem(
        memory_schema=ConversationMemory,
        key_extractor=lambda x: x.session_id,
        llm_client=None,
        embedder=None,
        strategy_or_merger=MergeStrategy.MERGE_FIELD,
    )

    # 添加所有对话回合到记忆中
    print("📚 处理对话回合...")
    conversation_memory.add(all_conversation_turns)
    print(f"   对话记忆已整合为{conversation_memory.size}条记录")

    # 检索综合记忆
    print("\n📖 AI对对话的综合记忆：")
    print("=" * 80)

    for session_id in ["conv_session_2024_001", "conv_session_2024_002"]:
        memory = conversation_memory.get(session_id)
        if memory:
            print(f"\n   📝 会话：{memory.session_id}")
            print(f"      用户：{memory.user_name}")

            print(f"      👤 已知兴趣：{len(memory.user_interests)}个领域")
            for interest in memory.user_interests:
                print(f"         • {interest}")

            print(f"\n      🎯 目标：{len(memory.goals_discussed)}个")
            for goal in memory.goals_discussed:
                print(f"         • {goal}")

            print(f"\n      ✅ 决策：{len(memory.decisions_made)}个")
            for decision in memory.decisions_made:
                print(f"         • {decision}")

            print(f"      💼 偏好：{', '.join(memory.user_preferences[:2]) or '无'}")
            print(f"      📝 主题：覆盖{len(memory.known_topics)}个")

    # 记忆统计
    print("\n📊 记忆统计（所有会话）：")
    print("-" * 80)
    total_sessions = len(set(m.session_id for m in all_conversation_turns))
    print(f"   对话总数：{total_sessions}")
    print(f"   记忆记录总数：{conversation_memory.size}")
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    conversation_folder = temp_dir / "conversation_memory"

    print(f"\n💾 正在将对话记忆保存到{conversation_folder.relative_to(temp_dir.parent)}...")
    conversation_memory.dump(str(conversation_folder))
    print("   ✅ 记忆已保留 - 对话上下文已保存")

    # 记忆统计
    print("\n📊 记忆统计：")
    print("-" * 80)
    if memory:
        total_facts = (
            len(memory.known_topics)
            + len(memory.user_preferences)
            + len(memory.user_interests)
            + len(memory.goals_discussed)
            + len(memory.decisions_made)
        )
        print(f"\n   累积的总事实数：{total_facts}")
        print(f"   主题：{len(memory.known_topics)}")
        print(f"   偏好：{len(memory.user_preferences)}")
        print(f"   兴趣：{len(memory.user_interests)}")
        print(f"   目标：{len(memory.goals_discussed)}")
        print(f"   决策：{len(memory.decisions_made)}")
        print(f"   开放问题：{len(memory.open_questions)}")

    print("\n💡 记忆演变洞察：")
    print("-" * 80)
    print("\n   一轮一轮地，AI的理解变得：")
    print("      ✓ 更具体（通用→机器学习→强化学习）")
    print("      ✓ 更完整（偏好、兴趣、目标都浮现出来）")
    print("      ✓ 更具可操作性（抽象目标→具体决策）")
    print("      ✓ 更有上下文（用户职业轨迹的完整图景）")

    print("\n" + "=" * 80)
    print("✨ AI记忆通过对话自然演变！")
    print("=" * 80)


if __name__ == "__main__":
    example_conversation_history()
