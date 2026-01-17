中文示例 / Chinese Examples
====================

这个目录包含所有 OMem 示例的中文翻译版本。每个示例演示 OMem 的不同功能和用例。

## 示例概览

### 📝 01_self_improving_debugger.py
**自我改进的调试器 - LLM 动力的错误合并**

展示如何使用基于 LLM 的合并策略（`LLM.BALANCED`）将多个错误遭遇合并成统一、可操作的解决方案。调试器从之前的经验中学习，并通过智能合并生成更好的解决方案。

**关键特性：**
- 基于LLM的合并策略用于智能合并
- 错误去重和解决方案改进
- 跨多个调试会话的学习
- 存储位置：`temp/debugger_memory/`

**数据项：**
- 2种不同的错误类型（ERR_MODULE_NOT_FOUND, ERR_ATTRIBUTE_ERROR）
- 每种错误类型多次遭遇

### 🎮 02_rpg_npc_memory.py
**RPG NPC 记忆系统 - 通过游戏构建角色档案**

演示在游戏玩法中累积和合并游戏世界NPC（非玩家角色）的记忆。每次玩家与NPC互动时，系统都会获得关于该NPC的新信息，并使用字段合并策略来构建完整的角色档案。

**关键特性：**
- 游戏场景中的增量内存构建
- 列表字段的合并（头衔、技能、声望事件）
- 关系和意见追踪
- 存储位置：`temp/npc_memory/`

**数据项：**
- 2个不同的玩家角色
- 每个玩家多个互动遭遇

### 📚 03_semantic_scholar.py
**语义学者 - 向量搜索和持久化**

构建一个具有语义搜索功能的研究论文库。用户可以通过内容相似性而不是仅仅关键字进行搜索，库在会话之间保持其状态。

**关键特性：**
- 向量搜索用于语义相似性（需要 OpenAI 嵌入）
- 关键字-值查找与向量搜索一起使用
- 论文和嵌入的持久化存储
- 批量索引和搜索操作
- 存储位置：`temp/scholar_library/`

**数据项：**
- 2个研究方向（NLP + 计算机视觉）
- 每个方向5篇论文

### 💼 04_multi_source_fusion.py
**多源数据融合 - 统一客户档案**

将来自多个系统（CRM、计费、支持、营销）的客户数据集成成统一的档案。当来自不同来源的数据冲突时，系统使用 LLM 来决定最准确的信息。

**关键特性：**
- 多系统数据集成
- 冲突解决的LLM支持
- 数据质量追踪
- 完整客户档案合并
- 存储位置：`temp/customer_unified_profile/`

**数据项：**
- 2个不同的客户
- 每个客户4个数据源

### 💬 05_conversation_history.py
**对话历史 - 多轮对话中的内存演变**

演示对话系统如何通过对话轮次累积和演变对用户的理解。每个用户输入都包含新信息（主题、偏好、兴趣、目标），系统通过字段合并来整合这些信息。

**关键特性：**
- 多轮对话中的增量学习
- 用户主题和偏好追踪
- 对话上下文保留
- 决策和开放问题管理
- 存储位置：`temp/conversation_memory/`

**数据项：**
- 2个不同的用户对话会话
- 每个会话3-4轮对话

## 运行示例

### 单个示例
```bash
python zh/01_self_improving_debugger.py
python zh/02_rpg_npc_memory.py
python zh/03_semantic_scholar.py
python zh/04_multi_source_fusion.py
python zh/05_conversation_history.py
```

### 所有示例
```bash
for file in zh/*.py; do python "$file"; done
```

## API 密钥配置

某些示例使用 OpenAI API 以获得最佳功能：
- **01_self_improving_debugger.py** - 使用 LLM.BALANCED 合并（可选）
- **03_semantic_Scholar.py** - 使用嵌入进行向量搜索（可选）
- **04_multi_source_fusion.py** - 使用 LLM 进行冲突解决（可选）

配置 API 密钥在项目根目录的 `.env` 文件中：
```
OPENAI_API_KEY=your_key_here
```

如果未配置 API 密钥，所有示例都将优雅地降级到非 LLM 功能。

## 对应的英文版本

所有这些示例也有英文版本可在 `examples/` 目录中获取。功能完全相同，但注释和输出使用英文。

## 内存持久化

所有示例都会将它们的内存状态保存到 `temp/` 目录中：
- `temp/debugger_memory/` - 调试日志
- `temp/npc_memory/` - NPC档案
- `temp/scholar_library/` - 研究论文
- `temp/customer_unified_profile/` - 客户数据
- `temp/conversation_memory/` - 对话上下文

每个目录包含：
- `memory.json` - 持久化的内存数据
- `metadata.json` - 关于内存的元数据
- `faiss_index/` - 向量索引（仅适用于支持向量搜索的示例）

## 下一步

- 📖 查看英文版本以了解实现细节
- 🔧 修改示例以处理您自己的数据
- 🚀 将 OMem 集成到您自己的应用程序中
