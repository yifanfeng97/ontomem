# 🧠 Ontomem: 自我整合的记忆系统

**Ontomem** 构建于*本体记忆*（Ontology Memory）的概念之上——为 AI 系统提供结构化、连贯的知识表示。

> **让你的 AI 智能体拥有"连贯"的记忆，而不仅仅是"碎片"的检索。**


<p align="center">
  <img src="../assets/fw.png" alt="Ontomem 框架图" width="700" />
</p>

[![PyPI 版本](https://img.shields.io/pypi/v/ontomem.svg)](https://pypi.org/project/ontomem/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI 下载数](https://img.shields.io/pypi/dm/ontomem.svg)](https://pypi.org/project/ontomem/)

传统的 RAG（检索增强生成）系统检索文本碎片。**Ontomem** 采用 Pydantic 模式维护**结构化实体**，并通过智能合并算法自动将碎片化的观察融合为完整的知识图谱节点。

**它不仅仅存储数据——它持续"消化"和"组织"数据。**


---

## ✨ 核心特性

### 🧩 Schema-First（模式优先）& 类型安全
基于 **Pydantic** 构建。所有记忆都是强类型对象。告别 `{"unknown": "dict"}` 的地狱，拥抱 IDE 自动补全和类型检查。

### 🔄 自动整合（Auto-Consolidation）
当你多次插入关于同一实体（相同 ID）的不同信息时，Ontomem 不会创建重复记录。它使用可配置的策略（字段覆盖、列表合并或 **LLM 驱动的智能融合**）将其智能合并为一条**黄金记录**。

### 🔍 混合搜索（Hybrid Search）
- **键值查询**：O(1) 精确实体访问
- **向量搜索**：内置 FAISS 索引用于语义相似性搜索，自动同步

### 💾 状态保持 & 持久化
将完整的记忆状态（结构化数据 + 向量索引）保存到磁盘，下次启动时可在秒级恢复。

---

## 🎯 使用场景

### 🤖 自我进化的 AI 智能体
在多轮对话中积累调试经验，逐步优化决策。

### 👤 个人知识图谱
从对话中构建活动的联系人档案，包括偏好、技能和交互历史。

### 🏢 企业数据中心
统一来自 CRM、电子邮件、支持工单和社交媒体的客户/员工记录。

### 📚 知识库整合
合并来自多个来源的重复或互补的信息，构建单一真实来源。

---

## 🚀 快速示例

```python
from ontomem import OMem, MergeStrategy
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 定义模式
class BugFixExperience(BaseModel):
    error_signature: str
    solutions: list[str]
    prevention_tips: str

# 初始化记忆
memory = OMem(
    memory_schema=BugFixExperience,
    key_extractor=lambda x: x.error_signature,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)

# 添加经验
memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: pandas",
    solutions=["pip install pandas"],
    prevention_tips="检查 requirements.txt"
))

# 查询
experience = memory.get("ModuleNotFoundError: pandas")
print(experience.solutions)  # 跨所有观察的自动合并！
```

---

## 📊 为什么选择 Ontomem？

| 特性 | 传统向量数据库 | Ontomem 🧠 |
|------|--------------|-----------|
| **存储单元** | 文本块 | **结构化对象** |
| **去重** | 手动或基于嵌入 | **原生、基于 ID** |
| **更新** | 仅追加（产生重复） | **自动合并（upsert）** |
| **查询结果** | 类似文本片段 | **完整实体** |
| **类型安全** | ❌ 无 | ✅ **Pydantic** |
| **索引同步** | 需手动同步 | ✅ **自动同步** |

---

## 🔗 下一步

- **[快速开始](quick-start.md)** - 5 分钟入门指南
- **[合并策略](../user-guide/merge-strategies.md)** - 了解不同的合并方法
- **[API 参考](../api/overview.md)** - 完整 API 文档

---

**由热爱记忆超越搜索的 AI 开发者用 ❤️ 构建。**
