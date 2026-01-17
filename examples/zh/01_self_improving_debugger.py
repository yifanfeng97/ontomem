"""自我改进的调试器 - 演示基于LLM的合并策略。

本例展示OMem如何使用LLM.BALANCED合并策略将多个错误遭遇合并成统一的、可操作的解决方案。
每次调试器遇到错误时，它会从以前的经验中学习，并通过智能合并生成更好的解决方案。

主要特性：
- 基于LLM的合并策略用于智能合并
- 错误去重和解决方案改进
- 跨多个调试会话的学习
"""

import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

from ontomem import OMem

# 加载环境变量 (OPENAI_API_KEY 如果可用)
load_dotenv()


class DebugLog(BaseModel):
    """调试日志条目，包含错误上下文和解决方案。"""

    error_id: str
    error_type: str
    error_message: str
    stack_trace: str | None = None
    solutions: list[str] = []
    attempted_fixes: list[str] = []
    root_cause: str | None = None


def example_self_improving_debugger():
    """演示基于LLM的调试和智能错误合并。"""
    print("\n" + "=" * 80)
    print("自我改进的调试器：基于LLM的错误合并")
    print("=" * 80)

    # 模拟多个错误（2种不同的错误类型）
    all_debug_logs = [
        # 错误类型1：ModuleNotFoundError - 多次遭遇
        DebugLog(
            error_id="ERR_MODULE_NOT_FOUND",
            error_type="ModuleNotFoundError",
            error_message="没有名为'numpy'的模块",
            stack_trace="文件 app.py，第5行 <module>\n    import numpy as np",
            solutions=["安装numpy: pip install numpy"],
            attempted_fixes=[],
            root_cause=None,
        ),
        DebugLog(
            error_id="ERR_MODULE_NOT_FOUND",
            error_type="ModuleNotFoundError",
            error_message="没有名为'numpy'的模块",
            stack_trace="文件 utils.py，第42行 calculate\n    result = np.array(data)",
            solutions=[
                "安装numpy: pip install numpy",
                "将numpy添加到requirements.txt",
            ],
            attempted_fixes=["运行 pip install numpy"],
            root_cause="依赖未安装",
        ),
        DebugLog(
            error_id="ERR_MODULE_NOT_FOUND",
            error_type="ModuleNotFoundError",
            error_message="没有名为'numpy'的模块",
            stack_trace="文件 vectorize.py，第8行 process\n    import numpy",
            solutions=[
                "安装numpy",
                "检查虚拟环境激活",
                "升级pip: pip install --upgrade pip",
            ],
            attempted_fixes=[
                "运行 pip install numpy",
                "检查venv激活",
            ],
            root_cause="依赖在venv中缺失",
        ),
        # 错误类型2：AttributeError - 不同的错误多次遭遇
        DebugLog(
            error_id="ERR_ATTRIBUTE_ERROR",
            error_type="AttributeError",
            error_message="'NoneType'对象没有属性'split'",
            stack_trace="文件 processor.py，第23行 process\n    parts = text.split()",
            solutions=["在调用split()之前检查text是否为None"],
            attempted_fixes=[],
            root_cause=None,
        ),
        DebugLog(
            error_id="ERR_ATTRIBUTE_ERROR",
            error_type="AttributeError",
            error_message="'NoneType'对象没有属性'split'",
            stack_trace="文件 parser.py，第15行 parse\n    tokens = data.split(',')",
            solutions=[
                "在split()之前添加None检查",
                "使用getattr并设置默认值",
            ],
            attempted_fixes=["添加了 if data is not None 检查"],
            root_cause="上游函数返回了None",
        ),
    ]

    print("\n📋 错误遭遇日志：")
    for i, encounter in enumerate(all_debug_logs, 1):
        print(f"\n  遭遇 {i} [{encounter.error_id}]：")
        print(f"    错误: {encounter.error_message}")
        print(f"    提议的解决方案: {len(encounter.solutions)}个")
        print(f"    尝试过的修复: {len(encounter.attempted_fixes)}个")

    # 用智能合并初始化OMem（如果API密钥可用）
    print("\n🤖 使用智能合并初始化调试器内存...")

    from ontomem.merger import MergeStrategy
    
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o-mini")
        print("   ✅ 找到OpenAI API密钥 - 使用基于LLM的合并")

        omem = OMem(
            memory_schema=DebugLog,
            key_extractor=lambda x: x.error_id,
            llm_client=llm,
            embedder=None,
            merge_strategy=MergeStrategy.LLM.BALANCED,
        )
    except Exception as e:
        print(f"   ⚠️  LLM不可用 ({type(e).__name__}) - 改用字段合并")
        omem = OMem(
            memory_schema=DebugLog,
            key_extractor=lambda x: x.error_id,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE,
        )

    # 将所有遭遇添加到内存
    print("\n📚 将错误遭遇添加到内存...")
    omem.add(all_debug_logs)
    print(f"   内存大小: {omem.size}")

    # 为每种错误类型检索合并后的调试日志
    print("\n🔍 合并后的调试日志（智能合并后）：")
    for error_id in ["ERR_MODULE_NOT_FOUND", "ERR_ATTRIBUTE_ERROR"]:
        consolidated = omem.get(error_id)
        if consolidated:
            print(f"\n   错误ID: {consolidated.error_id}")
            print(f"   错误类型: {consolidated.error_type}")
            print(f"   错误消息: {consolidated.error_message}")
            print(f"   根本原因: {consolidated.root_cause or '从多个遭遇推断'}")
            print(f"\n   📌 所有找到的解决方案：")
            for j, solution in enumerate(consolidated.solutions, 1):
                print(f"      {j}. {solution}")
            print(f"\n   ✓ 尝试过的修复：")
            for j, fix in enumerate(consolidated.attempted_fixes, 1):
                print(f"      {j}. {fix}")

    # 持久化到temp目录
    temp_dir = Path(__file__).parent.parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    memory_folder = temp_dir / "debugger_memory"

    print(f"\n💾 将调试器内存持久化到 {memory_folder.relative_to(temp_dir.parent)}...")
    omem.dump(str(memory_folder))
    print("   ✅ 内存已持久化")

    # 演示加载之前的内存
    print("\n📖 加载之前的调试器内存...")
    from ontomem.merger import MergeStrategy
    
    omem_restored = OMem(
        memory_schema=DebugLog,
        key_extractor=lambda x: x.error_id,
        llm_client=None,
        embedder=None,
        merge_strategy=MergeStrategy.FIELD_MERGE,
    )
    omem_restored.load(str(memory_folder))
    print(f"   ✅ 恢复的内存大小: {omem_restored.size}")

    # 显示每种错误类型的内存内容
    print("\n📚 恢复的错误数据库：")
    for error_id in ["ERR_MODULE_NOT_FOUND", "ERR_ATTRIBUTE_ERROR"]:
        restored_log = omem_restored.get(error_id)
        if restored_log:
            print(f"\n   [{error_id}]")
            print(f"      错误类型: {restored_log.error_type}")
            print(f"      解决方案数量: {len(restored_log.solutions)}")

    print("\n" + "=" * 80)
    print("✨ 调试器从多个遭遇中学习了！")
    print("=" * 80)


if __name__ == "__main__":
    example_self_improving_debugger()
