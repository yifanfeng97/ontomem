# 安装

Ontomem 的完整安装指南。

## 系统需求

- **Python**：3.11 或更高版本
- **OS**：Linux、macOS 或 Windows
- **内存**：最少 2GB RAM（大规模部署需要更多）

## 安装方法

### 方案 1：PyPI（用户推荐）

安装最新稳定版本：

```bash
pip install ontomem
```

### 方案 2：uv（开发者推荐）

快速的现代 Python 包管理器：

```bash
# 如果还未安装 uv
curl https://astral.sh/uv/install.sh | sh

# 安装 ontomem
uv add ontomem
```

### 方案 3：从源代码安装（开发）

```bash
# 克隆仓库
git clone https://github.com/yifanfeng97/ontomem.git
cd ontomem

# 开发模式安装
uv sync --group dev

# 或使用 pip
pip install -e .
```

## 可选依赖

### 用于 LLM 驱动的合并

如果想使用基于 LLM 的合并策略：

```bash
pip install langchain langchain-openai
```

### 用于向量搜索

FAISS 包含在基础安装中。对于 GPU 加速：

```bash
pip install faiss-gpu  # CUDA 启用的 FAISS（需要 NVIDIA GPU）
```

### 开发工具

为 Ontomem 做贡献：

```bash
uv sync --group dev
```

包括：
- `pytest` - 测试框架
- `mkdocs` - 文档生成
- `black` - 代码格式化
- `ruff` - 代码检查

## 验证

验证你的安装：

```python
from ontomem import OMem, MergeStrategy
print("✅ Ontomem 安装成功！")
```

或从命令行：

```bash
python -c "import ontomem; print(ontomem.__version__)"
```

## 故障排除

### ImportError: FAISS not found

```bash
pip install faiss-cpu
```

对于 GPU 支持（仅 NVIDIA）：

```bash
pip install faiss-gpu
```

### LangChain 问题

确保你有正确的版本：

```bash
pip install "langchain>=1.2.1" "langchain-openai>=1.1.6" "langchain-community>=0.4.1"
```

### Pydantic 版本冲突

Ontomem 需要 Pydantic 2.x：

```bash
pip install "pydantic>=2.12.5"
```

## 环境设置

### API 密钥

如果使用 LLM 功能，设置 OpenAI API 密钥：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

或在 Python 中：

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

### 虚拟环境（可选但推荐）

```bash
# 创建虚拟环境
python -m venv .venv

# 激活
source .venv/bin/activate  # 在 Windows 上: .venv\Scripts\activate

# 安装 ontomem
pip install ontomem
```

## 下一步

- 遵循[快速开始](quick-start.md)指南
- 查看[示例](../examples/examples-overview.md)
- 阅读 [API 参考](../api/overview.md)

---

**有问题？** 查看我们的 [FAQ](../faq.md) 或 [GitHub Issues](https://github.com/yifanfeng97/ontomem/issues)。
