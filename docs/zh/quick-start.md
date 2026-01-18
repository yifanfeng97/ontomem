# 快速开始

5 分钟快速上手 OntoMem。

## 安装

### 使用 pip

```bash
pip install ontomem
```

### 使用 uv（推荐）

```bash
uv add ontomem
```

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/yifanfeng97/ontomem.git
cd ontomem

# 安装包含开发依赖
uv sync --group dev
```

## 你的第一个记忆系统

### 第 1 步：定义模式

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ResearcherProfile(BaseModel):
    """研究人员档案。"""
    name: str  # 作为键
    affiliation: str
    research_interests: List[str]
    publications: List[str]
    last_updated: Optional[datetime] = None
```

### 第 2 步：初始化 OntoMem

```python
from ontomem import OMem, MergeStrategy
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 创建记忆实例
memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,  # 使用名字作为唯一键
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.FIELD_MERGE  # 从简单开始
)
```

### 第 3 步：添加数据

```python
# 添加研究人员档案
memory.add(ResearcherProfile(
    name="Yann LeCun",
    affiliation="Meta AI",
    research_interests=["深度学习", "卷积网络"],
    publications=["反向传播应用于手写邮编识别"]
))

memory.add(ResearcherProfile(
    name="Yoshua Bengio",
    affiliation="Mila",
    research_interests=["深度学习", "AI安全"],
    publications=["通过反向传播学习表示"]
))
```

### 第 4 步：查询

```python
# 获取精确匹配
researcher = memory.get("Yann LeCun")
print(f"找到: {researcher.name}")
print(f"研究兴趣: {researcher.research_interests}")
```

## 自动整合示例

这就是 OntoMem 的亮点——自动合并碎片化数据：

```python
# 第 1 天：了解 Yann LeCun
memory.add(ResearcherProfile(
    name="Yann LeCun",
    affiliation="Meta AI",
    research_interests=["深度学习"],
    publications=["图像识别的 CNN"]
))

# 第 2 天：关于同一个人的新信息
memory.add(ResearcherProfile(
    name="Yann LeCun",
    affiliation="Meta AI",  # 相同
    research_interests=["卷积网络"],  # 新细节
    publications=["反向传播论文"]  # 额外论文
))

# 查询整合后的记录
profile = memory.get("Yann LeCun")
print(profile.research_interests)
# 输出: ["深度学习", "卷积网络"]
# 输出: ["图像识别的 CNN", "反向传播论文"]
```

## 构建语义搜索索引

```python
# 构建向量索引
memory.build_index()

# 现在可以按语义搜索
results = memory.search("机器学习神经网络", k=5)

for researcher in results:
    print(f"- {researcher.name}: {researcher.research_interests}")
```

## 保存和恢复

```python
# 保存整个记忆状态
memory.dump("./my_researcher_memory")

# 稍后，在新的 Python 会话中：
new_memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
)

# 恢复
new_memory.load("./my_researcher_memory")

# 继续工作
researcher = new_memory.get("Yann LeCun")
print(researcher.research_interests)  # 仍在这里！
```

## 下一步

- 探索[合并策略](../user-guide/merge-strategies.md)了解更复杂的合并方式
- 查看[高级用法](../user-guide/advanced-usage.md)获取 LLM 驱动的整合
- 参见[示例](../examples/examples-overview.md)查看真实场景

---

**需要帮助？** 查看我们的 [FAQ](../faq.md) 或在 [GitHub](https://github.com/yifanfeng97/ontomem) 上提出问题。
