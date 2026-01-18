# 01: 自我改进的调试器

## 概述

一个 AI 调试智能体从遇到的每个 bug 中学习，构建不断发展的解决方案知识库。每当遇到相同的错误时，OntoMem 会使用 LLM 驱动的合并来整合以前的经验，生成更好的解决方案。

## 主题

**错误学习与整合**

## 策略

**LLM.BALANCED 智能合并**与整合

## 关键特性

- ✅ 多次遭遇同一类型的错误
- ✅ 基于 LLM 的解决方案智能合并
- ✅ 跨遭遇学习和综合
- ✅ 为未来调试会话持久化存储记忆
- ✅ 调试智慧的渐进式完善

## 数据结构

### DebugLog
```python
error_id: str                      # 唯一错误标识
error_type: str                    # 错误类型
error_message: str                 # 错误消息
stack_trace: str | None            # 堆栈跟踪
solutions: list[str]               # 找到的多个解决方案
attempted_fixes: list[str]         # 尝试过的修复
root_cause: str | None             # 推断的根本原因
```

## 使用场景

**AI 开发与调试**：调试助手学习每个错误，自动整合解决方案，并合成调试智慧，帮助开发者更快地解决问题。

**优势**：
- 自动知识累积
- 跨项目错误模式识别
- 随时间推移合成最佳实践
- 减少解决问题的时间

## 运行示例

```bash
cd examples/
python 01_self_improving_debugger.py
```

## 输出

结果存储在 `temp/debugger_memory/`：
- `memory.json`：包含合并解决方案的整合错误记录
- `metadata.json`：模式和统计信息

## 您将学到

1. **错误整合**：如何合并来自多个错误遭遇的信息
2. **LLM 驱动的合并**：使用 LLM 智能合成冲突的解决方案
3. **跨遭遇学习**：从多个类似问题构建智慧
4. **记忆持久化**：保存和检索整合知识

## 相关概念

- [合并策略](../user-guide/merge-strategies.md)
- [LLM 集成](../user-guide/llm-integration.md)
- [持久化](../user-guide/persistence.md)

## 后续示例

- [02: RPG NPC 记忆](02-rpg-npc-memory.md) - 基于字段的档案构建
- [04: 多源融合](04-multi-source-fusion.md) - 高级冲突解决
