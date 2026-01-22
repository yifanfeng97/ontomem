# 搜索能力

学习如何有效搜索你的记忆。

## 基于键的查询

使用唯一键进行快速、精确匹配：

```python
researcher = memory.get("Yann LeCun")
if researcher:
    print(f"找到: {researcher.name}")
```

**性能**: O(1) - 常数时间，速度非常快。

---

## 语义搜索

按意义而不是精确键查找实体：

```python
memory.build_index()
results = memory.search("深度学习研究论文", top_k=5)

for result in results:
    print(result.name, result.research_focus)
```

**性能**: O(n) 相似性计算 + FAISS 优化。

### 构建索引

```python
# 从头构建
memory.build_index()

# 强制重建（许多更新后有用）
memory.build_index(force=True)
```

### 搜索参数

```python
results = memory.search(
    query="人工智能",  # 自然语言查询
    top_k=10                # 返回前 10 个结果
)
```

- **query**：描述你要查找内容的自然语言字符串
- **top_k**：返回的前 k 个结果数量（默认：5）

---

## 组合搜索方法

```python
# 首先，使用语义搜索缩小范围
candidates = memory.search("机器学习", top_k=20)

# 然后，使用精确查询验证
specific = memory.get("Yann LeCun")

# 过滤结果
active_researchers = [r for r in candidates if r.is_active]
```

---

## 搜索最佳实践

1. **使用语义搜索进行发现** - 查找概念相关的项目
2. **使用键查询获取已知项目** - 直接访问更快
3. **改进查询词** - 更好的查询 = 更好的结果
4. **根据需要调整 k** - 从 k=5 开始，如需增加

在[高级用法](advanced-usage.md)中查看更多内容。
