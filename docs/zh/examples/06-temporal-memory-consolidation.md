# 06: 时序记忆整合

## 概述

使用**组合键**将一系列碎片化事件转化为单条"日汇总"记录。展示时间切片聚合，其中整天的事件整合为一个带有 LLM 合成摘要的连贯记录。

## 主题

**时间序列数据聚合**

## 策略

**时间切片 + LLM.BALANCED 合并**

## 关键特性

- ✅ 碎片化事件的日度聚合
- ✅ 使用组合键的时间分段
- ✅ 时间感知的整合
- ✅ LLM 合成的日汇总
- ✅ 跨时间的趋势分析

## 数据结构

### DailyTrace
```python
user: str                          # 用户标识
date: str                          # 日期 (YYYY-MM-DD)
actions: list[str]                 # 累积的操作
summary: str                       # LLM 合成的摘要
mood: str | None                   # 推断的心情/情感
key_events: list[str]              # 重要事件
productivity: str | None           # 生产力评估
notes: list[str]                   # 附加备注
```

## 使用场景

**分析与日志**：将流式日志、用户事件或遥测整合为日汇总。适用于仪表板、分析和跨时间段的趋势分析。

**优势**：
- 减少数据量（每天 1 个摘要而不是 1000 个事件）
- 更好的模式识别
- 高效的存储和检索
- 时间感知的洞察

## 运行示例

```bash
cd examples/

# 设置 OpenAI API 密钥用于 LLM 合成（可选）
export OPENAI_API_KEY="your-key-here"

python 06_temporal_memory_consolidation.py
```

## 输出

结果存储在 `temp/temporal_memory/`：
- `memory.json`：日汇总记录
- `metadata.json`：模式和统计信息
- `faiss_index/`：用于时间搜索的向量索引

## API 需求 🔄 可选

有 **OpenAI API 密钥**时此示例效果最好，用于 LLM 驱动的合成，但没有也能进行基础整合。

## 您将学到

1. **组合键**：使用组合键进行时间感知的分组
2. **时间切片**：将事件聚合到时间分段
3. **LLM 合成**：生成事件摘要
4. **时间模式**：发现跨时间的模式
5. **流处理**：处理连续事件流

## 复杂度

**⭐⭐⭐ 中级**：展示高级时间感知整合模式。

## 真实应用

- **日活动摘要**：将 1000 个用户操作转换为日文摘
- **系统监控**：将日志聚合为日健康报告
- **分析**：将事件流转换为可分析的日度指标
- **趋势分析**：识别跨天/周/月的模式

## 相关概念

- [组合键](../user-guide/key-extraction.md#composite-keys)
- [时间序列数据](../user-guide/advanced-usage.md#time-series)
- [合并策略](../user-guide/merge-strategies.md)
- [语义搜索](../user-guide/search-capabilities.md)

## 后续步骤

- 探索[高级用法](../user-guide/advanced-usage.md)了解更多模式
- 学习[持久化](../user-guide/persistence.md)
- 查看 [API 参考](../api/overview.md)
