# 示例概览

探索 6 个 OntoMem 的真实使用示例，展示不同的功能和用例。

## 特色示例

### 1️⃣ 自我改进的调试器
一个 AI 调试智能体从遇到的每个 bug 中学习，构建不断发展的解决方案知识库。

**主题**：错误学习与整合  
**策略**：LLM.BALANCED 智能合并  
**关键特性**：错误整合、LLM 驱动的合并、跨遭遇学习  
**[查看示例 →](01-self-improving-debugger.md)** | [源代码](../../../examples/01_self_improving_debugger.py)

---

### 2️⃣ RPG NPC 记忆
模拟 RPG 游戏中，NPC 通过多次交互来构建对玩家角色的记忆。

**主题**：角色档案构建  
**策略**：MERGE_FIELD（增量字段更新）  
**关键特性**：多种交互类型、渐进式声誉追踪、增量技能识别  
**[查看示例 →](02-rpg-npc-memory.md)** | [源代码](../../../examples/02_rpg_npc_memory.py)

---

### 3️⃣ 语义学者
构建一个可搜索的研究论文库，支持语义搜索功能。可以通过内容相似性而不仅仅是关键词来发现论文。

**主题**：学术论文库  
**策略**：向量搜索 + 持久化  
**关键特性**：向量嵌入、语义搜索（需要 OpenAI API）、元数据管理  
**[查看示例 →](03-semantic-scholar.md)** | [源代码](../../../examples/03_semantic_scholar.py)

---

### 4️⃣ 多源融合
将来自多个系统（CRM、账单、支持、营销）的客户信息整合到一个统一的档案中，使用智能合并处理冲突。

**主题**：客户数据整合  
**策略**：LLM.BALANCED 合并与冲突解决  
**关键特性**：多系统集成、自动冲突解决、数据质量报告、来源追踪  
**[查看示例 →](04-multi-source-fusion.md)** | [源代码](../../../examples/04_multi_source_fusion.py)

---

### 5️⃣ 对话历史
展示 AI 如何通过多轮对话来维护和演进对用户的理解。

**主题**：对话记忆演进  
**策略**：MERGE_FIELD 增量事实累积  
**关键特性**：逐轮更新、增量事实累积、上下文维护  
**[查看示例 →](05-conversation-history.md)** | [源代码](../../../examples/05_conversation_history.py)

---

### 6️⃣ 时序记忆整合
使用**组合键**将一系列碎片化事件转化为单条"日汇总"记录。

**主题**：时间序列数据聚合  
**策略**：时间切片 + LLM.BALANCED 合并  
**关键特性**：日度聚合、时间分段、时间感知整合  
**[查看示例 →](06-temporal-memory-consolidation.md)** | [源代码](../../../examples/06_temporal_memory_consolidation.py)

---

## 运行示例

所有示例都包含在 `examples/` 目录中：

```bash
# 进入 examples 目录
cd examples/

# 运行特定示例
python 01_self_improving_debugger.py
python 02_rpg_npc_memory.py
python 03_semantic_scholar.py
python 04_multi_source_fusion.py
python 05_conversation_history.py
python 06_temporal_memory_consolidation.py

# 中文版本
cd zh/
python 01_self_improving_debugger.py
```

---

## 功能矩阵

| # | 示例 | 主题 | 策略 | 复杂度 | 需要 API |
|---|------|------|------|-------|---------|
| 01 | 自我改进的调试器 | 错误学习 | LLM.BALANCED | ⭐⭐⭐ | 可选 |
| 02 | RPG NPC 记忆 | 角色档案 | MERGE_FIELD | ⭐⭐ | ❌ 否 |
| 03 | 语义学者 | 论文库 | 向量搜索 | ⭐⭐⭐ | ✅ 是 |
| 04 | 多源融合 | 数据整合 | LLM.BALANCED | ⭐⭐⭐⭐ | 可选 |
| 05 | 对话历史 | 聊天记忆 | MERGE_FIELD | ⭐⭐⭐ | ❌ 否 |
| 06 | 时序记忆 | 时间序列 | LLM.BALANCED | ⭐⭐⭐ | 可选 |

---

## 快速开始示例

查看[快速开始](../quick-start.md)指南了解立即可用的示例。

---

## 下一步

- 探索 [API 参考](../api/overview.md)
- 阅读[合并策略](../user-guide/merge-strategies.md)
- 查看 [FAQ](../faq.md)
