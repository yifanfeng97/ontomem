# 高级用法

掌握高级模式和优化技术。

## 批量操作

```python
# 高效添加许多项目
researchers = [r1, r2, r3, ..., r1000]
memory.add(researchers)  # 所有批量合并

# 查询属性
print(memory.keys)   # 所有唯一键
print(memory.items)  # 所有实体
print(memory.size)   # 总数
```

## 自定义键提取器

```python
# 复合键
key_extractor = lambda x: f"{x.first_name}_{x.last_name}"

# 不区分大小写
key_extractor = lambda x: x.email.lower()

# 基于哈希（用于敏感数据）
import hashlib
key_extractor = lambda x: hashlib.md5(x.id.encode()).hexdigest()
```

## 增量索引

```python
# 首先构建
memory.build_index()

# 添加新项 - 索引自动更新
memory.add(new_researcher)

# 如果需要手动重建
memory.build_index(force=True)
```

## 内存管理

```python
# 检查大小
print(f"记忆包含 {memory.size} 个实体")

# 如果需要清除
memory.clear()  # 删除所有数据和索引

# 删除特定项目
success = memory.remove("john_doe")
```

## 错误处理

```python
from ontomem import OMem, MergeStrategy

try:
    memory.add(item)
except Exception as e:
    print(f"错误: {e}")
    # 优雅处理
```

---

有关更多详情，请参阅 [API 参考](../api/overview.md)。
