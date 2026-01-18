# 02: RPG NPC 记忆

## 概述

模拟 RPG 游戏中，NPC 通过多次交互来构建对玩家角色的记忆。每次交互都会添加或更新关于玩家的信息，展示增量档案构建的方式。

## 主题

**角色档案构建**

## 策略

**FIELD_MERGE**（增量字段更新）

## 关键特性

- ✅ 多种交互类型（交易、战斗、对话）
- ✅ 字段级合并以确保档案完整性
- ✅ 渐进式声誉和关系追踪
- ✅ 增量技能和成就识别
- ✅ 位置感知的记忆追踪

## 数据结构

### NPCMemory
```python
player_id: str                     # 玩家唯一 ID
player_name: str | None            # 已知的玩家名字
titles_earned: list[str]           # 获得的称号
reputation_events: list[str]       # 重要事件
known_skills: list[str]            # 发现的技能
trade_history: list[dict]          # 交易历史
first_meeting_location: str | None # 第一次见面地点
last_known_location: str | None    # 最后已知位置
npc_opinion: str | None            # NPC 对玩家的看法
party_relationship: str | None     # 关系状态
```

## 使用场景

**游戏开发**：构建 NPC 记忆系统，追踪玩家交互，记住过去事件，基于累积经验演进关系。

**优势**：
- 真实的 NPC 玩家交互记忆
- 动态关系追踪
- 渐进式技能发现
- 持久的声誉系统

## 运行示例

```bash
cd examples/
python 02_rpg_npc_memory.py
```

## 输出

结果存储在 `temp/npc_memory/`：
- `memory.json`：每个玩家的 NPC 记忆记录
- `metadata.json`：模式和统计信息

## 您将学到

1. **增量更新**：通过多次交互渐进构建档案
2. **字段级合并**：合并单个字段同时保留列表信息
3. **关系追踪**：维持演进的关系和声誉
4. **游戏状态集成**：将 Ontomem 与游戏系统集成

## 无需 API ✅

此示例无需任何外部 API 密钥或依赖，仅需核心 Ontomem 包。

## 相关概念

- [合并策略](../user-guide/merge-strategies.md)
- [键值提取](../user-guide/key-extraction.md)

## 后续示例

- [03: 语义学者](03-semantic-scholar.md) - 向量搜索能力
- [05: 对话历史](05-conversation-history.md) - 对话中的类似档案构建
