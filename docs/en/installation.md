# 安装# Installation


































































































































































**有问题？** 查看我们的 [FAQ](../faq.md) 或 [GitHub Issues](https://github.com/yifanfeng97/ontomem/issues)。---- 阅读 [API 参考](../api/overview.md)- 查看[示例](../examples/examples-overview.md)- 遵循[快速开始](quick-start.md)指南## 下一步```pip install ontomem# 安装 ontomemsource .venv/bin/activate  # 在 Windows 上: .venv\Scripts\activate# 激活python -m venv .venv# 创建虚拟环境```bash### 虚拟环境（可选但推荐）```os.environ["OPENAI_API_KEY"] = "your-api-key-here"import os```python或在 Python 中：```export OPENAI_API_KEY="your-api-key-here"```bash如果使用 LLM 功能，设置 OpenAI API 密钥：### API 密钥## 环境设置```pip install "pydantic>=2.12.5"```bashOntoMem 需要 Pydantic 2.x：### Pydantic 版本冲突```pip install "langchain>=1.2.1" "langchain-openai>=1.1.6" "langchain-community>=0.4.1"```bash确保你有正确的版本：### LangChain 问题```pip install faiss-gpu```bash对于 GPU 支持（仅 NVIDIA）：```pip install faiss-cpu```bash### ImportError: FAISS not found## 故障排除```python -c "import ontomem; print(ontomem.__version__)"```bash或从命令行：```print("✅ OntoMem 安装成功！")from ontomem import OMem, MergeStrategy```python验证你的安装：## 验证- `ruff` - 代码检查- `black` - 代码格式化- `mkdocs` - 文档生成- `pytest` - 测试框架包括：```uv sync --group dev```bash为 OntoMem 做贡献：### 开发工具```pip install faiss-gpu  # CUDA 启用的 FAISS（需要 NVIDIA GPU）```bashFAISS 包含在基础安装中。对于 GPU 加速：### 用于向量搜索```pip install langchain langchain-openai```bash如果想使用基于 LLM 的合并策略：### 用于 LLM 驱动的合并## 可选依赖```pip install -e .# 或使用 pipuv sync --group dev# 开发模式安装cd ontomemgit clone https://github.com/yifanfeng97/ontomem.git# 克隆仓库```bash### 方案 3：从源代码安装（开发）```uv add ontomem# 安装 ontomemcurl https://astral.sh/uv/install.sh | sh# 如果还未安装 uv```bash快速的现代 Python 包管理器：### 方案 2：uv（开发者推荐）```pip install ontomem```bash安装最新稳定版本：### 方案 1：PyPI（用户推荐）## 安装方法- **内存**：最少 2GB RAM（大规模部署需要更多）- **OS**：Linux、macOS 或 Windows- **Python**：3.11 或更高版本## 系统需求OntoMem 的完整安装指南。
Complete installation guide for OntoMem.

## System Requirements

- **Python**: 3.11 or higher
- **OS**: Linux, macOS, or Windows
- **Memory**: Minimum 2GB RAM (more for large-scale deployments)

## Installation Methods

### Option 1: PyPI (Recommended for Users)

Install the latest stable release:

```bash
pip install ontomem
```

### Option 2: uv (Recommended for Developers)

Fast and modern Python package manager:

```bash
# Install uv if not already installed
curl https://astral.sh/uv/install.sh | sh

# Install ontomem
uv add ontomem
```

### Option 3: From Source (Development)

```bash
# Clone the repository
git clone https://github.com/yifanfeng97/ontomem.git
cd ontomem

# Install in development mode
uv sync --group dev

# Or with pip
pip install -e .
```

## Optional Dependencies

### For LLM-Powered Merging

If you want to use LLM-based merge strategies:

```bash
pip install langchain langchain-openai
```

### For Vector Search

FAISS is included in the base installation. For GPU acceleration:

```bash
pip install faiss-gpu  # CUDA-enabled FAISS (requires NVIDIA GPU)
```

### Development Tools

For contributing to OntoMem:

```bash
uv sync --group dev
```

This includes:
- `pytest` - Testing framework
- `mkdocs` - Documentation generation
- `black` - Code formatting
- `ruff` - Linting

## Verification

Verify your installation:

```python
from ontomem import OMem, MergeStrategy
print("✅ OntoMem installed successfully!")
```

Or from command line:

```bash
python -c "import ontomem; print(ontomem.__version__)"
```

## Troubleshooting

### ImportError: FAISS not found

```bash
pip install faiss-cpu
```

For GPU support (NVIDIA only):

```bash
pip install faiss-gpu
```

### LangChain Issues

Ensure you have the correct version:

```bash
pip install "langchain>=1.2.1" "langchain-openai>=1.1.6" "langchain-community>=0.4.1"
```

### Pydantic Version Conflicts

OntoMem requires Pydantic 2.x:

```bash
pip install "pydantic>=2.12.5"
```

## Environment Setup

### API Keys

If using LLM features, set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or in Python:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

### Virtual Environment (Optional but Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install ontomem
pip install ontomem
```

## Next Steps

- Follow the [Quick Start](quick-start.md) guide
- Check out [Examples](../examples/examples-overview.md)
- Read the [API Reference](../api/overview.md)

---

**Having issues?** Check our [FAQ](../faq.md) or [GitHub Issues](https://github.com/yifanfeng97/ontomem/issues).
