# API 概览

Ontomem 的完整 API 参考。

## 核心类：OMem

管理你的记忆系统的主类。

### 构造器

```python
OMem(
    memory_schema: Type[T],
    key_extractor: Callable[[T], Any],
    llm_client: Optional[BaseChatModel] = None,
    embedder: Optional[Embeddings] = None,
    merge_strategy: MergeStrategy = MergeStrategy.FIELD_MERGE
)
```

**参数：**

- `memory_schema` (Type[T])：定义实体结构的 Pydantic 模型
- `key_extractor` (Callable)：从实体中提取唯一键的函数
- `llm_client` (Optional)：用于 LLM 策略的 LangChain 聊天模型
- `embedder` (Optional)：用于语义搜索的 LangChain 嵌入
- `merge_strategy` (MergeStrategy)：如何处理冲突

### 核心方法

#### `add(items)`
向记忆添加一个或多个项目。自动合并重复。

```python
memory.add(researcher)  # 单个项目
memory.add([r1, r2, r3])  # 多个项目
```

#### `get(key)`
通过唯一键检索实体。

```python
researcher = memory.get("Yann LeCun")
```

**返回：** 实体或 None（如果未找到）。

#### `remove(key)`
通过键删除实体。

```python
success = memory.remove("Yann LeCun")
```

**返回：** bool - 如果删除为 True，如果未找到为 False。

#### `clear()`
删除所有实体并重置索引。

```python
memory.clear()
```

#### `build_index()`
为语义搜索构建或重建向量索引。

```python
memory.build_index()  # 从头构建
memory.build_index(force=True)  # 强制重建
```

#### `search(query, k=5)`
在实体上进行语义搜索。

```python
results = memory.search("深度学习神经网络", k=10)
```

**参数：**
- `query` (str)：自然语言搜索查询
- `k` (int)：结果数量

**返回：** 按语义相似性排名的前 k 个实体

#### `dump(folder_path)`
将记忆状态保存到磁盘。

```python
memory.dump("./my_memory")
# 创建：my_memory/memory.json, my_memory/faiss.index, 等
```

#### `load(folder_path)`
从磁盘加载记忆状态。

```python
memory.load("./my_memory")
```

### 属性

#### `keys`
获取记忆中的所有唯一键。

```python
all_keys = memory.keys  # List[Any]
```

#### `items`
获取所有实体实例。

```python
all_entities = memory.items  # List[T]
```

#### `size`
获取实体数量。

```python
count = memory.size  # int
```

---

## 枚举

### MergeStrategy

```python
from ontomem import MergeStrategy

class MergeStrategy(Enum):
    FIELD_MERGE = "field_merge"
    KEEP_INCOMING = "keep_incoming"
    KEEP_EXISTING = "keep_existing"
    
    class LLM(Enum):
        BALANCED = "llm_balanced"
        PREFER_INCOMING = "llm_prefer_incoming"
        PREFER_EXISTING = "llm_prefer_existing"
```

---

## 类型提示

### 泛型类型 T

所有实体必须是 Pydantic 模型：

```python
from pydantic import BaseModel

class Profile(BaseModel):
    id: str
    name: str
    age: int
```

### 可选类型

对于可选的依赖功能：

```python
from typing import Optional
from ontomem import OMem

# 如果不使用 LLM 策略，LLM 策略是可选的
llm_client: Optional[ChatModel] = None
embedder: Optional[Embeddings] = None
```

---

## 错误处理

### 常见异常

```python
from ontomem import OMem, MergeStrategy

# KeyError：键未找到
try:
    entity = memory.get("nonexistent")
except KeyError:
    print("实体未找到")

# ValueError：无效策略
try:
    memory = OMem(..., merge_strategy="invalid")
except ValueError:
    print("无效策略")

# RuntimeError：未配置 LLM
try:
    memory.add(entity)  # 带有 LLM.BALANCED 策略但没有 llm_client
except RuntimeError:
    print("LLM 客户端未配置")
```

---

## 示例

### 基础用法

```python
from ontomem import OMem, MergeStrategy
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings

class Researcher(BaseModel):
    name: str
    institution: str
    papers: list[str]

memory = OMem(
    memory_schema=Researcher,
    key_extractor=lambda x: x.name,
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.FIELD_MERGE
)

memory.add(Researcher(
    name="Yann LeCun",
    institution="Meta AI",
    papers=["CNNs"]
))

researcher = memory.get("Yann LeCun")
print(researcher.papers)
```

### 带 LLM 合并

```python
from langchain_openai import ChatOpenAI

memory = OMem(
    memory_schema=Researcher,
    key_extractor=lambda x: x.name,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    merge_strategy=MergeStrategy.LLM.BALANCED
)
```

---

## 版本信息

检查版本：

```python
import ontomem
print(ontomem.__version__)  # 例如 "0.1.2"
```

---

查看详细指南：

- [合并策略](../../user-guide/merge-strategies.md)
- [高级用法](../../user-guide/advanced-usage.md)
- [示例](../../examples/examples-overview.md)
