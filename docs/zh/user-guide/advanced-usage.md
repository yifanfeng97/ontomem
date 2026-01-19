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
## 高级用法：带动态上下文的自定义合并规则

使用 `MergeStrategy.LLM.CUSTOM_RULE` 创建针对你的领域定制的复杂合并策略。

### 时间感知的合并

```python
from datetime import datetime
from ontomem import OMem, MergeStrategy

# 定义一个根据时间调整合并行为的函数
def get_business_context():
    """根据营业时间调整合并策略。"""
    hour = datetime.now().hour
    day = datetime.now().weekday()
    
    if day >= 5:  # 周末
        return "周末模式：接受所有更新，优先考虑用户反馈而不是系统日志"
    elif hour < 9 or hour > 17:  # 非工作时间
        return "非工作时间模式：保守策略，优先选择稳定的历史数据"
    else:  # 工作时间
        return "工作时间模式：平衡最近的更新和已验证的历史数据"

memory = OMem(
    memory_schema=UserActivity,
    key_extractor=lambda x: x.user_id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.CUSTOM_RULE,
    rule="""
    合并用户活动记录：
    - 将所有唯一的操作合并到时间线中
    - 根据最新活动更新用户状态
    - 保留所有行为模式和异常
    """,
    dynamic_rule=get_business_context
)
```

### 环境特定的逻辑

```python
import os

def get_environment_rules():
    """根据部署环境调整合并规则。"""
    env = os.getenv("ENVIRONMENT", "dev")
    
    if env == "production":
        return """
        生产环境：使用严格合并。
        - 仅接受已验证的数据源
        - 需要证据来解决冲突信息
        - 维护数据完整性是首要任务
        """
    elif env == "staging":
        return """
        测试环境：中度合并。
        - 接受大多数进行某些验证的更新
        - 记录冲突用于调试
        - 允许实验
        """
    else:  # dev
        return """
        开发环境：宽松合并。
        - 接受所有传入数据
        - 快速迭代和测试
        - 记录所有内容以供检查
        """

memory = OMem(
    memory_schema=SystemConfig,
    key_extractor=lambda x: x.config_id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.CUSTOM_RULE,
    rule="智能合并系统配置更新",
    dynamic_rule=get_environment_rules
)
```

### 状态感知的多源整合

```python
class DataQualityState:
    """跟踪数据质量指标以支持上下文感知合并。"""
    def __init__(self):
        self.source_reliability = {
            "database": 0.95,
            "api": 0.85,
            "user_input": 0.60,
            "ml_inference": 0.75
        }

# 初始化状态跟踪器
quality_state = DataQualityState()

def get_data_quality_rules():
    """基于数据源质量生成合并规则。"""
    rules = "按质量权重合并数据：\n"
    for source, reliability in quality_state.source_reliability.items():
        rules += f"- {source}: {reliability*100}% 权重\n"
    rules += "冲突时优先选择高质量源"
    return rules

memory = OMem(
    memory_schema=CustomerRecord,
    key_extractor=lambda x: x.customer_id,
    llm_client=ChatOpenAI(model="gpt-4o"),
    embedder=OpenAIEmbeddings(),
    strategy_or_merger=MergeStrategy.LLM.CUSTOM_RULE,
    rule="从多个来源整合客户记录",
    dynamic_rule=get_data_quality_rules
)

# 随着可靠性的变化，未来的合并会自动调整
quality_state.source_reliability["user_input"] = 0.80  # 用户输入得到改进
memory.add(new_customer_record)  # 使用更新后的质量权重
```
---

有关更多详情，请参阅 [API 参考](../api/overview.md)。
