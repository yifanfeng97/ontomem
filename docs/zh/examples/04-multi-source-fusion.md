# 04: 多源融合

## 概述

将来自多个系统（CRM、账单、支持、营销）的客户信息整合到一个统一的档案中，使用智能合并处理冲突。展示了跨异构源的高级冲突解决和数据质量追踪。

## 主题

**客户数据整合**

## 策略

**LLM.BALANCED 合并与冲突解决**

## 关键特性

- ✅ 多系统数据整合
- ✅ 自动冲突检测和解决
- ✅ 数据质量报告和完整性追踪
- ✅ 来源追踪（记录哪个系统提供的数据）
- ✅ 跨部门统一客户视图

## 数据结构

### CustomerProfile
```python
customer_id: str                   # 客户 ID
name: str | None                   # 客户名字
email: str | None                  # 电子邮件
phone: str | None                  # 电话号码
company: str | None                # 公司/组织
job_title: str | None              # 职位
total_spending: float | None       # 终身花费
support_tickets: list[str]         # 支持工单 ID
preferred_products: list[str]      # 产品偏好
communication_preferences: list    # 首选通道
data_sources: list[str]            # 哪些系统提供了数据
last_updated: str | None           # 最后更新时间
```

## 使用场景

**企业数据管理**：将客户数据从 CRM、账单、支持和营销系统统一到单一黄金记录，通过智能冲突解决。

**优势**：
- 跨部门的单一客户视图
- 减少数据孤岛
- 自动冲突解决
- 数据质量提升
- 更好的客户体验

## 运行示例

```bash
cd examples/

# 设置 OpenAI API 密钥（可选，没有会回退）
export OPENAI_API_KEY="your-key-here"

python 04_multi_source_fusion.py
```

## 输出

结果存储在 `temp/customer_unified_profile/`：
- `memory.json`：统一的客户档案
- `metadata.json`：模式、统计和冲突日志

## API 需求 🔄 可选

有 **OpenAI API 密钥**时此示例效果最好，用于智能冲突解决，但没有也能正常运行。

## 您将学到

1. **多源整合**：合并来自多个异构源的数据
2. **冲突解决**：使用 LLM 智能解决矛盾
3. **数据质量**：追踪完整性和质量指标
4. **来源追踪**：记录每个数据来自哪个系统
5. **企业模式**：构建可扩展的数据统一系统

## 复杂度

**⭐⭐⭐⭐ 高级**：这是最复杂的示例，展示企业级数据整合模式。

## 相关概念

- [合并策略](../user-guide/merge-strategies.md)
- [LLM 集成](../user-guide/llm-integration.md)
- [冲突解决](../user-guide/merge-strategies.md#conflict-resolution)
- [持久化](../user-guide/persistence.md)

## 后续示例

- [05: 对话历史](05-conversation-history.md) - 渐进式档案构建
- [06: 时序记忆](06-temporal-memory-consolidation.md) - 时间感知聚合
