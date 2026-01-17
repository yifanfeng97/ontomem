"""Multi-Source Data Fusion - Demonstrates merging data from multiple external sources.

This example simulates a customer data integration system that consolidates
information from multiple sources (CRM, support tickets, transaction logs) into
a unified customer profile using OMem's intelligent merging capabilities.

Key Features:
- Merging heterogeneous data from multiple systems
- Conflict resolution through LLM-powered intelligent merging
- Data enrichment and deduplication
- Maintaining data lineage through source tracking
"""

import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

from ontomem import OMem

# Load environment variables (OPENAI_API_KEY if available)
load_dotenv()


class CustomerProfile(BaseModel):
    """Unified customer profile from multiple data sources."""

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
    """Demonstrate consolidating customer data from multiple sources."""
    print("\n" + "=" * 80)
    print("MULTI-SOURCE DATA FUSION: Unified Customer Profiles")
    print("=" * 80)

    # Collect data from 2 different customers across multiple sources
    all_customer_records = []

    # ===== CUSTOMER 1: Sarah Johnson =====
    # Data from CRM system
    all_customer_records.append(CustomerProfile(
        customer_id="cust_42857",
        name="Sarah Johnson",
        email="sarah.johnson@techcorp.com",
        phone=None,
        company="TechCorp Inc",
        job_title="Senior Product Manager",
        total_spending=None,
        support_tickets=[],
        preferred_products=["Enterprise Plan"],
        communication_preferences=["email"],
        data_sources=["CRM"],
        last_updated="2024-01-10",
    ))

    # Data from Transaction/Billing system
    all_customer_records.append(CustomerProfile(
        customer_id="cust_42857",
        name=None,
        email="s.johnson@techcorp.com",
        phone="555-1234",
        company=None,
        job_title=None,
        total_spending=45000.00,
        support_tickets=[],
        preferred_products=["Enterprise Plan", "Premium Support"],
        communication_preferences=["phone", "email"],
        data_sources=["Billing"],
        last_updated="2024-01-15",
    ))

    # Data from Support Ticketing system
    all_customer_records.append(CustomerProfile(
        customer_id="cust_42857",
        name="Sarah J.",
        email=None,
        phone="555-1234",
        company="TechCorp",
        job_title=None,
        total_spending=None,
        support_tickets=[
            "TICK-2024-001: API Integration help",
            "TICK-2024-005: Billing inquiry",
        ],
        preferred_products=["Enterprise Plan"],
        communication_preferences=["phone"],
        data_sources=["Support"],
        last_updated="2024-01-18",
    ))

    # Data from Marketing Analytics system
    all_customer_records.append(CustomerProfile(
        customer_id="cust_42857",
        name=None,
        email="sarah.johnson@techcorp.com",
        phone=None,
        company="TechCorp",
        job_title="Product Manager",
        total_spending=45000.00,
        support_tickets=[],
        preferred_products=["Enterprise Plan", "Data Analytics", "Custom Integration"],
        communication_preferences=["email"],
        data_sources=["Marketing"],
        last_updated="2024-01-12",
    ))

    # ===== CUSTOMER 2: Michael Chen =====
    # Data from CRM system
    all_customer_records.append(CustomerProfile(
        customer_id="cust_51892",
        name="Michael Chen",
        email="m.chen@startup.io",
        phone=None,
        company="InnovateLabs",
        job_title="CTO",
        total_spending=None,
        support_tickets=[],
        preferred_products=["Startup Pack"],
        communication_preferences=["email"],
        data_sources=["CRM"],
        last_updated="2024-01-05",
    ))

    # Data from Transaction/Billing system
    all_customer_records.append(CustomerProfile(
        customer_id="cust_51892",
        name=None,
        email="michael@innovatelabs.io",
        phone="555-5678",
        company=None,
        job_title=None,
        total_spending=12000.00,
        support_tickets=[],
        preferred_products=["Startup Pack", "Developer Tools"],
        communication_preferences=["phone"],
        data_sources=["Billing"],
        last_updated="2024-01-16",
    ))

    # Data from Support Ticketing system
    all_customer_records.append(CustomerProfile(
        customer_id="cust_51892",
        name="Michael C.",
        email=None,
        phone="555-5678",
        company="InnovateLabs",
        job_title=None,
        total_spending=None,
        support_tickets=["TICK-2024-003: Integration guide request"],
        preferred_products=["Startup Pack"],
        communication_preferences=["phone"],
        data_sources=["Support"],
        last_updated="2024-01-17",
    ))

    print("\n📊 Data from Multiple Sources (2 customers):")
    print("-" * 80)

    # Group by customer
    customers_data = {
        "cust_42857": ("Sarah Johnson", [r for r in all_customer_records if r.customer_id == "cust_42857"]),
        "cust_51892": ("Michael Chen", [r for r in all_customer_records if r.customer_id == "cust_51892"]),
    }

    for cust_id, (name, records) in customers_data.items():
        print(f"\n   Customer: {name} ({cust_id})")
        for i, record in enumerate(records, 1):
            print(f"      Source {i} ({record.data_sources[0]}): {record.name or record.email or 'unknown'}")

    # Initialize OMem with LLM-powered merging if available
    print("\n🔧 Initializing unified customer profile system...")
    from ontomem.merger import MergeStrategy

    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o-mini")
        print("   ✅ OpenAI API key found - using intelligent merging")

        customer_db = OMem(
            memory_schema=CustomerProfile,
            key_extractor=lambda x: x.customer_id,
            llm_client=llm,
            embedder=None,
            merge_strategy=MergeStrategy.LLM.BALANCED,
        )
    except Exception as e:
        print(f"   ⚠️  LLM not available - using field merge")
        customer_db = OMem(
            memory_schema=CustomerProfile,
            key_extractor=lambda x: x.customer_id,
            llm_client=None,
            embedder=None,
            merge_strategy=MergeStrategy.FIELD_MERGE,
        )

    # Merge all data sources
    print("\n📥 Merging data from all sources...")
    customer_db.add(all_customer_records)
    print(f"   Merged into {customer_db.size} unified profile(s)")

    # Retrieve unified profiles
    print("\n✨ Unified Customer Profiles:")
    print("-" * 80)

    for cust_id in ["cust_42857", "cust_51892"]:
        unified = customer_db.get(cust_id)
        if unified:
            print(f"\n   Customer ID: {unified.customer_id}")
            print(f"   📋 Personal Information:")
            print(f"      Name: {unified.name}")
            print(f"      Email: {unified.email}")
            print(f"      Phone: {unified.phone}")
            print(f"      Job Title: {unified.job_title}")

            print(f"\n   🏢 Company Information:")
            print(f"      Company: {unified.company}")

            print(f"\n    💰 Business Metrics:")
            print(f"      Total Spending: ${unified.total_spending:,.2f}")
            print(f"      Support Tickets: {len(unified.support_tickets)}")

            print(f"\n    📦 Product Preferences: {', '.join(unified.preferred_products)}")
            print(f"    💬 Communication: {', '.join(unified.communication_preferences)}")
            print(f"   📍 Data Sources: {', '.join(unified.data_sources)}")
            print(f"   ⏱️  Last Updated: {unified.last_updated}")

    # Summary statistics
    print("\n\n📈 Customer Database Summary:")
    print("-" * 80)
    print(f"   Total Customers: {customer_db.size}")
    total_spending = sum(
        c.total_spending for c in [customer_db.get(cid) for cid in ["cust_42857", "cust_51892"]]
        if c and c.total_spending
    )
    print(f"   Total Combined Spending: ${total_spending:,.2f}")
    print(f"   All Unique Sources Integrated: CRM, Billing, Support, Marketing")

    # Persist unified profile
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    profile_folder = temp_dir / "customer_unified_profile"

    print(f"\n💾 Saving unified profile to {profile_folder.relative_to(temp_dir.parent)}...")
    customer_db.dump(str(profile_folder))
    print("   ✅ Profile persisted for future reference")

    # Show integration benefits
    print("\n🎯 Integration Benefits:")
    print("-" * 80)
    print("   ✓ Single source of truth for customer data")
    print("   ✓ Automatic conflict resolution via LLM")
    print("   ✓ Real-time profile updates across systems")
    print("   ✓ Improved customer experience through unified view")
    print("   ✓ Data quality monitoring and reconciliation")

    print("\n" + "=" * 80)
    print("✨ Customer data successfully unified!")
    print("=" * 80)


if __name__ == "__main__":
    example_multi_source_fusion()
