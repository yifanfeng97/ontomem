"""多源数据融合 - 演示从多个外部源合并数据。

此示例模拟了一个客户数据集成系统，将来自多个源
（CRM、支持工单、交易日志）的信息整合到统一的客户档案中，
使用OMem的智能合并功能。

主要特性：
- 合并来自多个系统的异构数据
- 通过LLM驱动的智能合并进行冲突解决
- 数据丰富和去重
- 通过源跟踪维护数据谱系
"""

import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

from ontomem import OMem

# 加载环境变量（如果可用则加载OPENAI_API_KEY）
load_dotenv()


class CustomerProfile(BaseModel):
    """来自多个数据源的统一客户档案。"""

    customer_id: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    job_title: str | None = None
    total_spending: float | None = None
    support_tickets: list[str] = []
    preferred_products: list[str] = []
    communication_preferences: list[str] = []
    data_sources: list[str] = []
    last_updated: str | None = None


def example_multi_source_fusion():
    """演示从多个源整合客户数据。"""
    print("\n" + "=" * 80)
    print("多源数据融合：统一的客户档案")
    print("=" * 80)

    # 收集来自多个源的2个不同客户的数据
    all_customer_records = []

    # ===== 客户1：莎拉·约翰逊 =====
    # 来自CRM系统的数据
    all_customer_records.append(CustomerProfile(
        customer_id="cust_42857",
        name="莎拉·约翰逊",
        email="sarah.johnson@techcorp.com",
        phone=None,
        company="TechCorp Inc",
        job_title="高级产品经理",
        total_spending=None,
        support_tickets=[],
        preferred_products=["企业计划"],
        communication_preferences=["电子邮件"],
        data_sources=["CRM"],
        last_updated="2024-01-10",
    ))

    # 来自交易/账单系统的数据
    all_customer_records.append(CustomerProfile(
        customer_id="cust_42857",
        name=None,
        email="s.johnson@techcorp.com",
        phone="555-1234",
        company=None,
        job_title=None,
        total_spending=45000.00,
        support_tickets=[],
        preferred_products=["企业计划", "高级支持"],
        communication_preferences=["电话", "电子邮件"],
        data_sources=["账单"],
        last_updated="2024-01-15",
    ))

    # 来自支持工单系统的数据
    all_customer_records.append(CustomerProfile(
        customer_id="cust_42857",
        name="莎拉·约翰逊",
        email=None,
        phone="555-1234",
        company="TechCorp",
        job_title=None,
        total_spending=None,
        support_tickets=[
            "工单-2024-001：API集成帮助",
            "工单-2024-005：账单查询",
        ],
        preferred_products=["企业计划"],
        communication_preferences=["电话"],
        data_sources=["支持"],
        last_updated="2024-01-18",
    ))

    # 来自营销分析系统的数据
    all_customer_records.append(CustomerProfile(
        customer_id="cust_42857",
        name=None,
        email="sarah.johnson@techcorp.com",
        phone=None,
        company="TechCorp",
        job_title="产品经理",
        total_spending=45000.00,
        support_tickets=[],
        preferred_products=["企业计划", "数据分析", "自定义集成"],
        communication_preferences=["电子邮件"],
        data_sources=["营销"],
        last_updated="2024-01-12",
    ))

    # ===== 客户2：迈克尔·陈 =====
    # 来自CRM系统的数据
    all_customer_records.append(CustomerProfile(
        customer_id="cust_51892",
        name="迈克尔·陈",
        email="m.chen@startup.io",
        phone=None,
        company="创新实验室",
        job_title="首席技术官",
        total_spending=None,
        support_tickets=[],
        preferred_products=["初创包"],
        communication_preferences=["电子邮件"],
        data_sources=["CRM"],
        last_updated="2024-01-05",
    ))

    # 来自交易/账单系统的数据
    all_customer_records.append(CustomerProfile(
        customer_id="cust_51892",
        name=None,
        email="michael@innovatelabs.io",
        phone="555-5678",
        company=None,
        job_title=None,
        total_spending=12000.00,
        support_tickets=[],
        preferred_products=["初创包", "开发者工具"],
        communication_preferences=["电话"],
        data_sources=["账单"],
        last_updated="2024-01-16",
    ))

    # 来自支持工单系统的数据
    all_customer_records.append(CustomerProfile(
        customer_id="cust_51892",
        name="迈克尔·陈",
        email=None,
        phone="555-5678",
        company="创新实验室",
        job_title=None,
        total_spending=None,
        support_tickets=["工单-2024-003：集成指南请求"],
        preferred_products=["初创包"],
        communication_preferences=["电话"],
        data_sources=["支持"],
        last_updated="2024-01-17",
    ))

    print("\n📊 来自多个源的数据（2个客户）：")
    print("-" * 80)

    # 按客户分组
    customers_data = {
        "cust_42857": ("莎拉·约翰逊", [r for r in all_customer_records if r.customer_id == "cust_42857"]),
        "cust_51892": ("迈克尔·陈", [r for r in all_customer_records if r.customer_id == "cust_51892"]),
    }

    for cust_id, (name, records) in customers_data.items():
        print(f"\n   客户：{name}（{cust_id}）")
        for i, record in enumerate(records, 1):
            print(f"      源 {i}（{record.data_sources[0]}）：{record.name or record.email or '未知'}")

    # 初始化OMem，使用LLM驱动的合并（如果可用）
    print("\n🔧 初始化统一客户档案系统...")
    from ontomem.merger import MergeStrategy

    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o-mini")
        print("   ✅ 找到了OpenAI API密钥 - 使用智能合并")

        customer_db = OMem(
            memory_schema=CustomerProfile,
            key_extractor=lambda x: x.customer_id,
            llm_client=llm,
            embedder=None,
            merge_strategy=MergeStrategy.LLM.BALANCED,
        )
    except Exception as e:
        print(f"   ⚠️  LLM不可用 - 使用字段合并")
        customer_db = OMem(
            memory_schema=CustomerProfile,
            key_extractor=lambda x: x.customer_id,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.MERGE_FIELD,
        )

    # 合并所有数据源
    print("\n📥 正在从所有源合并数据...")
    customer_db.add(all_customer_records)
    print(f"   已整合为{customer_db.size}个统一档案")

    # 检索统一档案
    print("\n✨ 统一的客户档案：")
    print("-" * 80)

    for cust_id in ["cust_42857", "cust_51892"]:
        unified = customer_db.get(cust_id)
        if unified:
            print(f"\n   客户ID：{unified.customer_id}")
            print(f"   📋 个人信息：")
            print(f"      名字：{unified.name}")
            print(f"      电子邮件：{unified.email}")
            print(f"      电话：{unified.phone}")
            print(f"      职位：{unified.job_title}")

            print(f"\n   🏢 公司信息：")
            print(f"      公司：{unified.company}")

            print(f"\n    💰 商业指标：")
            print(f"      总消费：${unified.total_spending:,.2f}")
            print(f"      支持工单：{len(unified.support_tickets)}")

            print(f"\n    📦 产品偏好：{', '.join(unified.preferred_products)}")
            print(f"    💬 通信方式：{', '.join(unified.communication_preferences)}")
            print(f"   📍 数据源：{', '.join(unified.data_sources)}")
            print(f"   ⏱️  最后更新：{unified.last_updated}")

    # 摘要统计
    print("\n\n📈 客户数据库摘要：")
    print("-" * 80)
    print(f"   客户总数：{customer_db.size}")
    total_spending = sum(
        c.total_spending for c in [customer_db.get(cid) for cid in ["cust_42857", "cust_51892"]]
        if c and c.total_spending
    )
    print(f"   总消费：${total_spending:,.2f}")
    print(f"   所有集成的独特源：CRM、账单、支持、营销")

    # 保留统一档案
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    profile_folder = temp_dir / "customer_unified_profile"

    print(f"\n💾 正在将统一档案保存到{profile_folder.relative_to(temp_dir.parent)}...")
    customer_db.dump(str(profile_folder))
    print("   ✅ 档案已保留以供将来参考")

    # 显示集成优势
    print("\n🎯 集成优势：")
    print("-" * 80)
    print("   ✓ 客户数据的单一事实来源")
    print("   ✓ 通过LLM自动冲突解决")
    print("   ✓ 跨系统的实时档案更新")
    print("   ✓ 通过统一视图改进客户体验")
    print("   ✓ 数据质量监控和协调")

    print("\n" + "=" * 80)
    print("✨ 客户数据已成功统一！")
    print("=" * 80)


if __name__ == "__main__":
    example_multi_source_fusion()
