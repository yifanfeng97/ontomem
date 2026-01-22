# 持久化

保存和恢复你的记忆状态。

## 保存记忆

使用 `dump()` 将你的整个记忆状态保存到磁盘：

```python
memory.dump("./my_memory")
```

这会创建：
- `memory.json` - 你的序列化实体
- `faiss_index/` - 向量索引目录（如果已构建）
- `metadata.json` - 配置和元数据

## 加载记忆

恢复已保存的记忆状态：

```python
# 使用相同的模式创建新的记忆实例
new_memory = OMem(
    memory_schema=ResearcherProfile,
    key_extractor=lambda x: x.name,
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.MERGE_FIELD
)

# 加载已保存的状态
new_memory.load("./my_memory")

# 你的数据被恢复了！
print(new_memory.size)  # 显示实体数量
```

## 文件结构

```
my_memory/
├── memory.json           # 序列化的实体
├── metadata.json         # 配置和元数据
└── faiss_index/          # 向量索引目录（如果已构建）
    ├── index.faiss
    └── docstore.pkl
```

## 细粒度持久化 (v0.1.5+)

为了对保存内容有更多控制，可以使用细粒度方法：

### 仅保存数据
```python
# 只保存结构化数据，不保存索引或元数据
memory.dump_data("./my_data.json")
```

### 仅保存索引
```python
# 只保存向量索引
memory.dump_index("./my_index_folder")
```

### 仅保存元数据
```python
# 只保存元数据
memory.dump_metadata("./my_metadata.json")
```

### 仅加载数据
```python
# 只加载结构化数据
new_memory.load_data("./my_data.json")
```

### 仅加载索引
```python
# 只加载向量索引
new_memory.load_index("./my_index_folder")
```

### 仅加载元数据
```python
# 只加载元数据
new_memory.load_metadata("./my_metadata.json")
```

### 选择性备份策略
```python
# 分别备份数据和索引
memory.dump_data("./backups/data_v1.json")
memory.dump_index("./backups/index_v1")

# 仅恢复数据，重新构建索引
new_memory.load_data("./backups/data_v1.json")
new_memory.build_index()
```

## 备份和恢复

```python
# 创建带时间戳的备份
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
memory.dump(f"./backups/memory_{timestamp}")

# 列表和恢复
import os
backups = os.listdir("./backups")
latest = sorted(backups)[-1]
memory.load(f"./backups/{latest}")
```

## 导出到标准格式

```python
import json
import pandas as pd

# 导出为 JSON
with open("export.json", "w") as f:
    data = [item.model_dump() for item in memory.items]
    json.dump(data, f, indent=2)

# 导出为 CSV
df = pd.DataFrame([item.model_dump() for item in memory.items])
df.to_csv("export.csv", index=False)

# 导出为 Parquet（用于大型数据集）
df.to_parquet("export.parquet")
```

---

下一步：探索[高级用法](advanced-usage.md)。
