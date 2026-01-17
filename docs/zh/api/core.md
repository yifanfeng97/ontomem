# 概览

Ontomem 为构建智能记忆系统提供了一个全面、结构良好的 API。本部分涵盖核心模块和类。

## 核心模块

### `ontomem.core`
包含 OMem 类和基类的主模块。

- **OMem**：主记忆管理类
- **BaseMem**：记忆实现的抽象基类

### `ontomem.merger`
冲突解决的合并策略实现。

- **经典策略**：基于字段的合并、保留传入、保留现有
- **LLM 策略**：智能综合、基于偏好的合并

### `ontomem.utils`
实用函数和帮助程序。

- **Logging**：结构化日志记录工具
- **Type helpers**：常见类型定义

---

## 详细的模块文档

有关特定模块的详细信息：

- [Core Module](core.md)
- [Merger Module](merger.md)
- [Utils Module](utils.md)

---

查看[快速开始](../../quick-start.md)立即开始。
