# 🧠 Ontomem: 自我整合的记忆层

[English](README.md) | 中文版本

**Ontomem** 构建于*本体记忆*（Ontology Memory）的概念之上——为 AI 系统提供结构化、连贯的知识表示。

> **让你的 AI 智能体拥有"连贯"的记忆，而不仅仅是"碎片"的检索。**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

传统的 RAG（检索增强生成）系统检索文本碎片。**Ontomem** 采用 Pydantic 模式维护**结构化实体**，并通过智能合并算法自动将碎片化的观察融合为完整的知识图谱节点。

**它不仅仅存储数据——它持续"消化"和"组织"数据。**

---

## ✨ 为什么选择 Ontomem？

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

## 🚀 快速开始：构建"自我进化"的经验库

想象一个 AI 调试智能体。没有记忆时，它每次都重复相同的试错过程。有了 **Ontomem**，它构建一份持久的**"调试手册"**，随着遇到的每个新问题而进化。

### 1. 定义你的经验模式

```python
from pydantic import BaseModel
from typing import List, Optional

class BugFixExperience(BaseModel):
    """一份活动的调试知识记录。"""
    error_signature: str            # 键：例如 "ModuleNotFoundError: pandas"
    root_causes: List[str]          # 这个错误可能发生的不同原因
    solutions: List[str]            # 发现的多个解决方案
    prevention_tips: str            # 综合理解如何避免此问题
    last_updated: Optional[str] = None
```

### 2. 初始化带有 LLM 驱动合并的 Ontomem

我们使用 `LLM.BALANCED` 策略，这样 Ontomem 不仅列出解决方案——它**综合**它们成为连贯、可行的指导。

```python
from ontomem import OMem, MergeStrategy
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

experience_memory = OMem(
    memory_schema=BugFixExperience,
    key_extractor=lambda x: x.error_signature,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)
```

### 3. 智能体随时间学习

#### 第 1 天：首次遭遇
智能体遇到 pandas 的 `ModuleNotFoundError`，用 `pip install` 修复。

```python
# 经验 1：初始观察
experience_memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: No module named 'pandas'",
    root_causes=["环境中缺少库"],
    solutions=["运行: pip install pandas"],
    prevention_tips="运行代码前始终检查 requirements.txt。"
))
```

#### 第 2 天：新环境，不同解决方案
智能体在 Docker 容器中遇到同样错误，但 pip 失败，系统包管理器 `apt-get install python3-pandas` 成功。

```python
# 经验 2：不同环境，相同错误
experience_memory.add(BugFixExperience(
    error_signature="ModuleNotFoundError: No module named 'pandas'",
    root_causes=["系统 Python 中不存在包", "pip 的二进制不兼容性"],
    solutions=["运行: apt-get install python3-pandas", "在容器中使用系统包管理器"],
    prevention_tips="在容器化环境中，对编译依赖优先使用系统包。"
))
```

#### 第 3 天：智能体寻求智慧
当新的智能体实例遇到同样错误时，它查询进化的知识库：

```python
# 检索综合智慧
guidance = experience_memory.get("ModuleNotFoundError: No module named 'pandas'")

print("根本原因:")
for cause in guidance.root_causes:
    print(f"  - {cause}")
# 输出：
#   - 环境中缺少库
#   - 系统 Python 中不存在包
#   - pip 的二进制不兼容性

print("\n解决方案:")
for i, solution in enumerate(guidance.solutions, 1):
    print(f"  {i}. {solution}")
# 输出：
#   1. 运行: pip install pandas（标准方法）
#   2. 运行: apt-get install python3-pandas（系统 Python）
#   3. 在容器中使用系统包管理器

print("\n预防提示:")
print(guidance.prevention_tips)
# 输出: "运行代码前检查 requirements.txt。
#       在容器中，对编译依赖优先使用系统包。
#       考虑使用虚拟环境隔离依赖。"
```

#### 第 4 天：语义搜索类似问题
智能体不记得确切的错误，但可以按概念搜索：

```python
# 语义搜索：查找与导入相关的问题
similar_issues = experience_memory.search(
    "Python 模块导入失败 依赖缺失",
    k=5
)

print(f"找到 {len(similar_issues)} 个相关的调试经验")
```

**智能体从"试错"进化到"明智决策"。无需样板代码。无需手动整合。只需添加经验，让 Ontomem 综合智慧。**

---

## 🔍 语义搜索

构建索引并通过自然语言搜索：

```python
# 构建向量索引
experience_memory.build_index()

# 语义搜索
results = experience_memory.search("调试 Python 异常堆栈溢出", k=5)

for experience in results:
    print(f"- {experience.error_signature}")
    print(f"  解决方案: {experience.solutions}")
```

---

## 🛠️ 合并策略

选择如何处理冲突：

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| `FIELD_MERGE` | 非空覆盖、列表追加 | 简单属性收集 |
| `KEEP_NEW` | 最新数据优先 | 状态更新（当前角色、最后在线时间） |
| `KEEP_OLD` | 首个观察保留 | 历史记录（首次发布年份） |
| `LLM.BALANCED` | **LLM 驱动的语义合并** | 复杂综合、矛盾解决 |

```python
# 示例：LLM 智能合并冲突的分析
memory = OMem(
    ...,
    merge_strategy=MergeStrategy.LLM.BALANCED
)
```

---

## 💾 保存与加载

快照你的完整记忆状态：

```python
# 保存（结构化数据 → memory.json，向量 → FAISS 索引）
experience_memory.dump("./debug_knowledge")

# 稍后快速恢复
new_memory = OMem(...)
new_memory.load("./debug_knowledge")
```

---

## 📊 Ontomem vs 传统方法

| 特性 | 传统向量数据库 | Ontomem 🧠 |
|------|--------------|-----------|
| **存储单元** | 文本块 | **结构化对象** |
| **去重** | 手动或基于嵌入 | **原生、基于 ID** |
| **更新** | 仅追加（产生重复） | **自动合并（upsert）** |
| **查询结果** | 类似文本片段 | **完整实体** |
| **类型安全** | ❌ 无 | ✅ **Pydantic** |
| **索引同步** | 需手动同步 | ✅ **自动同步** |

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

## 🔧 安装

### 基础安装

```bash
pip install ontomem
```

或使用 `uv`：
```bash
uv add ontomem
```

### 为开发者

要设置包含所有测试和文档工具的开发环境：

```bash
uv sync --group dev
```

**核心需求：**
- Python 3.11+
- LangChain（用于 LLM 集成）
- Pydantic（用于模式定义）
- FAISS（用于向量搜索）

---

## 📚 API 参考

### 核心方法

#### `add(items: Union[T, List[T]]) → None`
添加项目到记忆。自动按键合并重复项。

```python
experience_memory.add(BugFixExperience(...))
experience_memory.add([exp1, exp2, exp3])
```

#### `get(key: Any) → Optional[T]`
按键检索实体。

```python
experience = experience_memory.get("ModuleNotFoundError: pandas")
```

#### `build_index(force: bool = False) → None`
为语义搜索构建或重建向量索引。

```python
experience_memory.build_index()  # 如果干净则构建
experience_memory.build_index(force=True)  # 强制重建
```

#### `search(query: str, k: int = 5) → List[T]`
在所有实体上进行语义搜索。

```python
results = experience_memory.search("依赖管理错误", k=10)
```

#### `dump(folder_path: Union[str, Path]) → None`
将记忆状态（数据 + 索引）保存到磁盘。

```python
experience_memory.dump("./my_knowledge")
```

#### `load(folder_path: Union[str, Path]) → None`
从磁盘加载记忆状态。

```python
experience_memory.load("./my_knowledge")
```

#### `remove(key: Any) → bool`
按键删除实体。

```python
success = experience_memory.remove("ModuleNotFoundError: pandas")
```

#### `clear() → None`
清除所有实体和索引。

```python
experience_memory.clear()
```

### 属性

#### `keys: List[Any]`
记忆中的所有唯一键。

#### `items: List[T]`
所有实体实例。

#### `size: int`
实体数量。

---

## 🤝 贡献

我们在构建下一代 AI 记忆标准。欢迎 PR 和 Issue！

---

## 📝 许可证

MIT 许可证 - 详见 LICENSE 文件。

---

**由热爱记忆超越搜索的 AI 开发者用 ❤️ 构建。**
