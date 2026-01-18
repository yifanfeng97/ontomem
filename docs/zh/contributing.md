# 贡献指南

我们欢迎对 OntoMem 的贡献！以下是入门方式。

## 开发设置

```bash
# 克隆仓库
git clone https://github.com/yifanfeng97/ontomem.git
cd ontomem

# 安装开发依赖
uv sync --group dev
```

## 进行更改

1. 创建功能分支：`git checkout -b feature/your-feature`
2. 进行更改
3. 运行测试：`pytest tests/`
4. 格式化代码：`black .`
5. 提交：`git commit -m "Add feature description"`
6. 推送：`git push origin feature/your-feature`
7. 创建拉取请求

## 代码风格

- 使用 `black` 进行格式化
- 使用 `ruff` 进行代码检查
- 遵循 PEP 8
- 为函数添加文档字符串

## 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_core.py

# 运行覆盖率测试
pytest --cov=ontomem tests/
```

## 文档

- 为新功能更新文档字符串
- 如果添加新功能，更新 README
- 构建文档：`mkdocs serve`

## Issues 和讨论

- **Bug 报告**：[GitHub Issues](https://github.com/yifanfeng97/ontomem/issues)
- **功能请求**：[GitHub Issues](https://github.com/yifanfeng97/ontomem/issues)
- **问题**：[GitHub Discussions](https://github.com/yifanfeng97/ontomem/discussions)

---

感谢你的贡献！🚀
