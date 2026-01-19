# 常见问题 (FAQ)

## 安装和设置

### Q: 系统需求是什么？

**A:** OntoMem 需要：
- Python 3.11 或更高版本
- 最少 2GB RAM
- 任何操作系统：Linux、macOS 或 Windows

### Q: 我需要单独安装 FAISS 吗？

**A:** 不需要，FAISS 包含在基础安装中（`faiss-cpu`）。

对于 GPU 加速（仅 NVIDIA）：
```bash
pip install faiss-gpu
```

### Q: 我可以在不使用 LLM 功能的情况下使用 OntoMem 吗？

**A:** 可以！LLM 功能是可选的。你可以使用经典合并策略（MERGE_FIELD、KEEP_INCOMING、KEEP_EXISTING）而无需任何 LLM 客户端或嵌入器。

---

## 使用问题

### Q: 我如何定义我的数据模式？

**A:** 使用 Pydantic BaseModel：

```python
from pydantic import BaseModel
from typing import List, Optional

class MyEntity(BaseModel):
    id: str  # 唯一标识符
    name: str
    tags: List[str]
    metadata: Optional[dict] = None
```

### Q: 我应该用什么作为 key_extractor？

**A:** 任何唯一标识实体的字段（或组合）：

```python
# 简单：使用单个字段
key_extractor=lambda x: x.id

# 复合：组合多个字段
key_extractor=lambda x: f"{x.first_name}_{x.last_name}"

# 复杂：自定义逻辑
key_extractor=lambda x: x.email.lower().split("@")[0]
```

### Q: 自动合并如何工作？

**A:** 当你添加具有现有键的实体时：

1. **触发合并**（不创建重复）
2. **策略**确定如何解决冲突
3. **结果**是单个整合的实体

```python
memory.add(v1)  # 添加
memory.add(v1_updated)  # 触发合并，不重复
```

### Q: MERGE_FIELD 和 LLM.BALANCED 的区别是什么？

**A:**

- **MERGE_FIELD**：简单、确定性（非空覆盖）
- **LLM.BALANCED**：智能综合，可以解决复杂矛盾，较慢并消耗 LLM tokens

使用 MERGE_FIELD 来提高速度/降低成本。使用 LLM.BALANCED 处理复杂数据。

---

## 搜索和检索

### Q: 我如何搜索我的记忆？

**A:** 两种方法：

```python
# 1. 精确查询（快速）
entity = memory.get("john_doe")

# 2. 语义搜索（需要索引）
memory.build_index()
results = memory.search("人工智能研究", k=5)
```

### Q: 我必须构建索引才能使用记忆吗？

**A:** 不。你可以在不构建索引的情况下使用 `get()`。索引仅在 `search()` 时需要。

### Q: 使用 search() 时应该检索多少个结果？

**A:** 取决于你的用例：
- `k=1-5`：查找最相关的单个项目
- `k=5-10`：获取顶部候选项
- `k=20+`：检索大型候选集

从 `k=5` 开始，根据结果调整。

---

## 持久化

### Q: 我如何保存我的记忆？

**A:** 使用 `dump()`：

```python
memory.dump("./my_memory")
# 创建：my_memory/memory.json, my_memory/faiss.index, 等
```

### Q: 我如何恢复已保存的记忆？

**A:** 使用 `load()`：

```python
new_memory = OMem(...)  # 使用相同模式创建实例
new_memory.load("./my_memory")  # 恢复状态
```

### Q: dump() 创建了哪些文件？

**A:**
- `memory.json`：序列化的实体
- `faiss.index`：向量索引（如果已构建）
- `metadata.json`：配置信息

### Q: 我可以将记忆导出为 JSON/CSV 吗？

**A:** 可以，手动操作：

```python
import json

# 导出为 JSON
with open("export.json", "w") as f:
    data = [item.model_dump() for item in memory.items]
    json.dump(data, f)

# 导出为 CSV
import pandas as pd
df = pd.DataFrame([item.model_dump() for item in memory.items])
df.to_csv("export.csv", index=False)
```

---

## 性能和扩展

### Q: OntoMem 可以处理多少个实体？

**A:** 取决于：
- 可用 RAM
- 实体大小
- 搜索需求

指南：
- **<100K 实体**：没有问题
- **100K-1M 实体**：监控 RAM，考虑批处理
- **>1M 实体**：考虑分片或专门向量数据库

### Q: 语义搜索是否很慢？

**A:** 不是：
- 构建索引：每个实体约 0.5-1ms
- 搜索：典型查询约 10-100ms
- 使用 MERGE_FIELD 合并：<1ms
- 使用 LLM 策略合并：约 1-2 秒（LLM 调用开销）

### Q: 我应该重建索引吗？

**A:** 在主要更新后：
```python
memory.build_index(force=True)  # 从头重建
```

否则，它会自动增量更新。

---

## 集成和 LLM

### Q: 支持哪些 LLM 提供商？

**A:** 任何 LangChain 兼容模型：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- 开源（通过 Ollama、HuggingFace）

```python
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")

# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-opus")

# Ollama
from langchain_community.chat_models import ChatOllama
llm = ChatOllama(model="llama2")
```

### Q: 我如何设置我的 API 密钥？

**A:**

```bash
# 环境变量
export OPENAI_API_KEY="sk-..."

# 或在代码中
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

### Q: 我应该使用哪个嵌入模型？

**A:** 受欢迎的选择：

```python
from langchain_openai import OpenAIEmbeddings
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# 开源
from langchain_community.embeddings import HuggingFaceEmbeddings
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

---

## 故障排除

### Q: 我收到"ImportError: FAISS not found"

**A:**
```bash
pip install faiss-cpu
# 或者 GPU：
pip install faiss-gpu
```

### Q: LLM 合并非常慢

**A:** 这是预期的。LLM 调用每次合并需要 1-2 秒。对于频繁操作使用经典策略。

### Q: 我的搜索结果不相关

**A:** 尝试：
1. 检查嵌入模型（使用更好的嵌入）
2. 增加 `k` 以获取更多候选项
3. 检查搜索查询质量

### Q: 我收到重复的实体

**A:** 验证 `key_extractor` 正确标识唯一实体：

```python
# 检查键是否真正唯一
keys = memory.keys
if len(keys) != len(set(keys)):
    print("检测到重复键！")
```

### Q: 内存消耗很高

**A:** 
- 检查实体大小（如果太大则使用总结）
- 考虑批处理/分片
- 定期重建索引

---

## 贡献和开发

### Q: 我如何为 OntoMem 做贡献？

**A:**
1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 添加测试
5. 提交 PR

查看[贡献](../contributing.md)指南。

### Q: 我如何运行测试？

**A:**
```bash
uv sync --group dev
pytest tests/
```

### Q: 我如何构建文档？

**A:**
```bash
uv add --group dev mkdocs mkdocs-material
mkdocs serve
```

---

## 其他问题

### Q: OntoMem 是否可用于生产？

**A:** OntoMem 目前处于版本 0.1.4（alpha）。它适合实验和开发。在生产中使用时要谨慎并进行彻底测试。

### Q: 路线图是什么？

**A:** 查看 [GitHub Issues](https://github.com/yifanfeng97/ontomem/issues) 了解计划的功能。

### Q: 我如何报告 bug？

**A:** 在 [GitHub 上开启 issue](https://github.com/yifanfeng97/ontomem/issues/new)。

---

**仍有问题？** 在 [GitHub Discussions](https://github.com/yifanfeng97/ontomem/discussions) 上提问。
