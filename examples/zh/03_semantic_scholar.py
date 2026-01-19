"""语义学者 - 演示向量搜索和持久化功能。

此示例构建了一个具有语义搜索功能的研究论文库。
用户可以根据内容相似性而不仅仅是关键字来搜索论文，
并且该库为未来的会话保留其状态。

主要特性：
- 语义相似性的向量搜索（需要OpenAI嵌入）
- 与向量搜索并行的键值查找
- 论文和嵌入的持久化存储
- 批量索引和搜索操作
"""

import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

from ontomem import OMem

# 加载环境变量（如果可用则加载OPENAI_API_KEY）
load_dotenv()


class ResearchPaper(BaseModel):
    """研究论文的元数据和摘要。"""

    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    year: int
    citations: int = 0
    keywords: list[str] = []
    related_papers: list[str] = []


def example_semantic_scholar():
    """演示论文库中的语义搜索和持久化。"""
    print("\n" + "=" * 80)
    print("语义学者：具有向量搜索功能的研究论文库")
    print("=" * 80)

    # 示例研究论文 - 自然语言处理焦点
    nlp_papers = [
        ResearchPaper(
            paper_id="nlp_001",
            title="注意力就是你所需要的一切",
            authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
            abstract="主流的序列转导模型基于复杂的循环或卷积神经网络。我们提出了一种新的简单网络架构，完全基于注意力机制，摈弃了递推和卷积。",
            year=2017,
            citations=88000,
            keywords=["transformer", "attention", "自然语言处理"],
            related_papers=["nlp_002", "nlp_003"],
        ),
        ResearchPaper(
            paper_id="nlp_002",
            title="BERT：深度双向Transformer的预训练",
            authors=["Devlin, J.", "Chang, M.", "Lee, K."],
            abstract="我们介绍BERT，一种预训练语言表示的方法，在广泛的自然语言处理任务上获得了最先进的结果。",
            year=2018,
            citations=65000,
            keywords=["BERT", "语言模型", "预训练"],
            related_papers=["nlp_001", "nlp_004"],
        ),
        ResearchPaper(
            paper_id="nlp_003",
            title="语言模型是无监督的多任务学习器",
            authors=["Radford, A.", "Wu, J.", "Child, R."],
            abstract="GPT-2演示了语言模型在新数据集上训练时，在没有任何显式监督的情况下开始学习这些任务。",
            year=2019,
            citations=26000,
            keywords=["GPT-2", "语言生成", "无监督"],
            related_papers=["nlp_001", "nlp_005"],
        ),
        ResearchPaper(
            paper_id="nlp_004",
            title="RoBERTa：经过稳健优化的BERT预训练方法",
            authors=["Liu, Y.", "Ott, M.", "Goyal, N."],
            abstract="我们介绍RoBERTa，一种优化的自监督语言模型预训练方法，包含关键的训练流程修改。",
            year=2019,
            citations=15000,
            keywords=["RoBERTa", "BERT", "优化"],
            related_papers=["nlp_002", "nlp_001"],
        ),
        ResearchPaper(
            paper_id="nlp_005",
            title="GPT-3：语言模型是少样本学习器",
            authors=["Brown, T.", "Mann, B.", "Ryder, N."],
            abstract="最近的工作通过在多样化的语料库上预训练并在特定任务上进行微调，在许多自然语言处理任务和基准上取得了显著的进展。",
            year=2020,
            citations=35000,
            keywords=["GPT-3", "少样本学习", "语言模型"],
            related_papers=["nlp_003", "nlp_001"],
        ),
    ]

    # 示例研究论文 - 计算机视觉焦点
    cv_papers = [
        ResearchPaper(
            paper_id="cv_001",
            title="一张图像值1000个16x16的字：用于图像识别的Transformer",
            authors=["Dosovitskiy, A.", "Beyer, L.", "Kolesnikov, A."],
            abstract="虽然Transformer架构已成为自然语言处理的事实标准，但其在计算机视觉中的应用仍然有限。我们表明，直接应用于图像块序列的纯Transformer在图像分类任务上表现很好。",
            year=2020,
            citations=22000,
            keywords=["vision transformer", "图像分类", "transformer"],
            related_papers=["cv_002", "cv_003"],
        ),
        ResearchPaper(
            paper_id="cv_002",
            title="Swin Transformer：使用移动窗口的分层视觉Transformer",
            authors=["Liu, Z.", "Lin, Y.", "Cao, Y."],
            abstract="一个称为Swin Transformer的新型视觉Transformer，可以充分用作计算机视觉的通用骨干。Swin Transformer通过用基于移动窗口的注意力模块替换每个Transformer块中的标准多头自注意力模块来构建。",
            year=2021,
            citations=15000,
            keywords=["Swin", "分层", "视觉"],
            related_papers=["cv_001", "cv_004"],
        ),
        ResearchPaper(
            paper_id="cv_003",
            title="掩盖自编码器是可扩展的视觉学习器",
            authors=["He, K.", "Chen, X.", "Xie, S."],
            abstract="本文表明掩盖自编码器（MAE）是计算机视觉的可扩展自监督学习器。我们的MAE方法很简单：我们掩盖输入图像的随机块并重建丢失的像素。",
            year=2021,
            citations=8000,
            keywords=["自监督", "视觉", "掩盖"],
            related_papers=["cv_001", "cv_005"],
        ),
        ResearchPaper(
            paper_id="cv_004",
            title="DeiT：数据高效的图像Transformer",
            authors=["Touvron, H.", "Cord, M.", "Douze, M."],
            abstract="图像分类方面的最近进展，无论是在学术界还是工业界，都是由从自然语言处理改进的Transformer模型驱动的。然而，这些视觉Transformer的计算密集度很高，与卷积神经网络相比，在达到高精度时需要明显更多的数据。",
            year=2020,
            citations=10000,
            keywords=["DeiT", "高效", "数据高效"],
            related_papers=["cv_001", "cv_002"],
        ),
        ResearchPaper(
            paper_id="cv_005",
            title="DINO：自监督视觉Transformer中的新兴特性",
            authors=["Caron, M.", "Touvron, H.", "Misra, I."],
            abstract="我们研究视觉Transformer的新兴自监督特性，并观察它们包含关于图像区域和类的明确语义信息。我们提出DINO，一种基于自监督学习和无标签知识蒸馏的方法。",
            year=2021,
            citations=6000,
            keywords=["DINO", "自监督", "蒸馏"],
            related_papers=["cv_001", "cv_003"],
        ),
    ]

    all_papers = nlp_papers + cv_papers

    print("\n📚 加载研究论文：")
    print("\n   📝 自然语言处理研究方向：")
    for paper in nlp_papers:
        print(f"      [{paper.paper_id}] {paper.title} ({paper.year})")

    print("\n   🖼️  计算机视觉方向：")
    for paper in cv_papers:
        print(f"      [{paper.paper_id}] {paper.title} ({paper.year})")

    # 初始化OMem
    print("\n🔧 正在初始化论文库...")
    from ontomem.merger import MergeStrategy
    
    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS

        embedder = OpenAIEmbeddings(model="text-embedding-3-small")
        print("   ✅ 找到了OpenAI API密钥 - 已启用向量搜索")

        library = OMem(
            memory_schema=ResearchPaper,
            key_extractor=lambda x: x.paper_id,
            llm_client=None,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )
    except Exception as e:
        print(f"   ⚠️  OpenAI不可用 - 仅使用关键字搜索")
        library = OMem(
            memory_schema=ResearchPaper,
            key_extractor=lambda x: x.paper_id,
            llm_client=None,
            embedder=None,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )

    # 将论文添加到库中
    print("\n📖 正在向统一研究库添加论文...")
    library.add(all_papers)
    print(f"   库中的论文总数：{library.size}")
    print(f"      • 自然语言处理论文：{len(nlp_papers)}")
    print(f"      • 计算机视觉论文：{len(cv_papers)}")

    # 从两个方向按ID检索
    print("\n🔍 直接查找（来自两个方向的论文）：")
    sample_papers = ["nlp_001", "cv_001"]
    for paper_id in sample_papers:
        paper = library.get(paper_id)
        if paper:
            track = "自然语言处理" if paper_id.startswith("nlp") else "计算机视觉"
            print(f"\n   [{track}] {paper.title}")
            print(f"      摘要：{paper.abstract[:80]}...")
            print(f"      引用次数：{paper.citations:,}")

    # 演示语义搜索（如果嵌入可用）
    print("\n🎯 语义搜索示例：")
    print("-" * 80)

    search_queries = [
        "Transformer神经网络",
        "视觉图像识别",
        "自监督学习",
    ]

    for query in search_queries:
        print(f"\n   查询：'{query}'")
        try:
            # 尝试语义搜索
            results = library.search(query, k=2)
            if results:
                print("   结果（按语义相似性排序）：")
                for i, paper_result in enumerate(results, 1):
                    print(f"      {i}. {paper_result.title}")
                    print(f"         方向：{'自然语言处理' if paper_result.paper_id.startswith('nlp') else '计算机视觉'}")
            else:
                print("   （语义搜索需要OpenAI API密钥）")
        except Exception:
            # 后备：关键字搜索
            matching = [
                p
                for p in all_papers
                if any(kw.lower() in query.lower() for kw in p.keywords)
            ]
            if matching:
                print("   结果（按关键字匹配）：")
                for i, p in enumerate(matching[:2], 1):
                    print(f"      {i}. {p.title}")

    # 将库保存到磁盘
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    library_folder = temp_dir / "scholar_library"

    print(f"\n💾 正在将库保存到{library_folder.relative_to(temp_dir.parent)}...")
    library.dump(str(library_folder))
    print("   ✅ 库已保存")

    # 统计数据
    print("\n📊 库的统计数据：")
    print("-" * 80)
    total_citations = sum(p.citations for p in all_papers)
    avg_year = sum(p.year for p in all_papers) / len(all_papers)
    all_keywords = set()
    for p in all_papers:
        all_keywords.update(p.keywords)

    print(f"   论文总数：{len(all_papers)}")
    print(f"      • 自然语言处理研究：{len(nlp_papers)}篇论文（{sum(p.citations for p in nlp_papers):,}次引用）")
    print(f"      • 计算机视觉：{len(cv_papers)}篇论文（{sum(p.citations for p in cv_papers):,}次引用）")
    print(f"\n   总引用数：{total_citations:,}")
    print(f"   平均发表年份：{avg_year:.0f}")
    print(f"   独特关键字：{len(all_keywords)}")
    print(f"   最被引用的论文：{max(all_papers, key=lambda p: p.citations).title}")

    # 显示热门关键字
    keyword_freq = {}
    for p in all_papers:
        for kw in p.keywords:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

    print(f"\n   热门关键字（跨所有方向）：")
    for kw, freq in sorted(keyword_freq.items(), key=lambda x: -x[1])[:5]:
        print(f"      • {kw}：{freq}篇论文")

    print("\n" + "=" * 80)
    print("✨ 研究论文库已准备好进行探索！")
    print("=" * 80)


if __name__ == "__main__":
    example_semantic_scholar()
