# 05: 对话历史

## 概述

展示 AI 如何通过多轮对话来维护和演进对用户的理解。每一轮都添加或完善知识，展示对话系统中增量记忆构建。

## 主题

**对话记忆演进**

## 策略

**FIELD_MERGE 增量事实累积**

## 关键特性

- ✅ 逐轮记忆更新
- ✅ 增量事实累积
- ✅ 自动上下文维护
- ✅ 记忆感知的响应生成
- ✅ 用户偏好追踪

## 数据结构

### ConversationMemory
```python
session_id: str                    # 对话会话 ID
user_name: str | None              # 用户名
known_topics: list[str]            # 讨论的主题
user_preferences: list[str]        # 明确的偏好
user_interests: list[str]          # 推断的兴趣
communication_style: str | None    # 首选风格
problem_history: list[str]         # 以前的问题
solutions_applied: list[str]       # 尝试过的方案
session_count: int                 # 会话数
last_interaction: str | None       # 最后更新时间
```

## 使用场景

**对话 AI 与聊天机器人**：构建聊天机器人和对话系统，记住用户偏好、追踪对话历史，通过累积知识随时间改进响应。

**优势**：
- 基于历史的个性化响应
- 减少重复解释上下文的需要
- 渐进式信任构建
- 改善用户体验

## 运行示例

```bash
cd examples/
python 05_conversation_history.py
```

## 输出

结果存储在 `temp/conversation_memory/`：
- `memory.json`：对话记忆记录
- `metadata.json`：模式和统计信息

## 无需 API ✅

此示例无需任何外部 API 密钥或依赖，仅需核心 Ontomem 包。

## 您将学到

1. **多轮更新**：跨对话轮更新记忆
2. **增量累积**：通过对话渐进构建档案
3. **上下文维护**：保持对话上下文追踪
4. **偏好追踪**：记录用户偏好和兴趣
5. **对话集成**：将 Ontomem 与聊天系统集成

## 复杂度

**⭐⭐⭐ 中级**：展示实用的对话系统集成模式。

## 相关概念

- [合并策略](../user-guide/merge-strategies.md)
- [自动整合](../user-guide/auto-consolidation.md)
- [持久化](../user-guide/persistence.md)

## 后续示例

- [02: RPG NPC 记忆](02-rpg-npc-memory.md) - 游戏中的类似档案构建
- [06: 时序记忆](06-temporal-memory-consolidation.md) - 基于时间的聚合
