# 03: 语义学者

## 概述

构建一个可搜索的研究论文库，支持语义搜索功能。可以通过内容相似性而不仅仅是关键词来发现论文。展示了混合搜索的威力，结合精确查询与语义相似性。

## 主题

**学术论文库**

## 策略

**向量搜索 + 持久化**

## 关键特性

- ✅ 用于语义搜索的向量嵌入（需要 OpenAI API）
- ✅ 元数据管理（引用、关键词、关系）
- ✅ 库统计和分析
- ✅ 索引论文的持久化存储
- ✅ 快速检索和发现

## 数据结构

### ResearchPaper
```python
paper_id: str                      # 论文唯一 ID
title: str                         # 论文标题
authors: list[str]                 # 作者名单
abstract: str                      # 论文摘要
year: int                          # 发表年份
citations: int                     # 引用数
keywords: list[str]                # 研究关键词
related_papers: list[str]          # 相关论文 ID
```

## 使用场景

**学术与研究系统**：构建可搜索的研究数据库，研究人员可通过语义相似性发现相关工作。不仅仅是关键词匹配，还有概念相似性。

**优势**：
- 发现超越关键词匹配的相关研究
- 自动论文推荐
- 研究趋势追踪
- 文献综述加速

## 运行示例

```bash
cd examples/

# 设置 OpenAI API 密钥
export OPENAI_API_KEY="your-key-here"

python 03_semantic_scholar.py
```

## 输出

结果存储在 `temp/scholar_library/`：
- `memory.json`：带有元数据的论文记录
- `metadata.json`：模式和统计信息
- `faiss_index/`：用于语义搜索的向量索引

## API 需求 ✅ 必需

此示例需要 **OpenAI API 密钥**来生成嵌入。

## 您将学到

1. **向量嵌入**：如何使用嵌入进行语义搜索
2. **混合搜索**：结合键值查询与语义相似性
3. **FAISS 索引**：持久化向量索引管理
4. **相似性搜索**：通过语义含义查找相关项

## 相关概念

- [语义搜索](../user-guide/search-capabilities.md)
- [向量索引](../user-guide/vector-indexing.md)
- [持久化](../user-guide/persistence.md)

## 后续示例

- [04: 多源融合](04-multi-source-fusion.md) - 高级数据整合
- [06: 时序记忆](06-temporal-memory-consolidation.md) - 时间序列模式
