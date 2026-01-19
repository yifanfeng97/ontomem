"""Semantic Scholar - Demonstrates vector search and persistence capabilities.

This example builds a research paper library with semantic search capabilities.
Users can search for papers by content similarity rather than just keywords,
and the library persists its state for future sessions.

Key Features:
- Vector search for semantic similarity (requires OpenAI embeddings)
- Key-value lookup alongside vector search
- Persistent storage of papers and embeddings
- Batch indexing and search operations
"""

import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

from ontomem import OMem

# Load environment variables (OPENAI_API_KEY if available)
load_dotenv()


class ResearchPaper(BaseModel):
    """Research paper metadata and abstract."""

    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    year: int
    citations: int = 0
    keywords: list[str] = []
    related_papers: list[str] = []


def example_semantic_scholar():
    """Demonstrate semantic search and persistence in a paper library."""
    print("\n" + "=" * 80)
    print("SEMANTIC SCHOLAR: Research Paper Library with Vector Search")
    print("=" * 80)

    # Sample research papers - NLP Focus
    nlp_papers = [
        ResearchPaper(
            paper_id="nlp_001",
            title="Attention Is All You Need",
            authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
            abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
            year=2017,
            citations=88000,
            keywords=["transformer", "attention", "NLP"],
            related_papers=["nlp_002", "nlp_003"],
        ),
        ResearchPaper(
            paper_id="nlp_002",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin, J.", "Chang, M.", "Lee, K."],
            abstract="We introduce BERT, a method of pre-training language representations that obtains state-of-the-art results on a wide array of Natural Language Processing tasks.",
            year=2018,
            citations=65000,
            keywords=["BERT", "language model", "pretraining"],
            related_papers=["nlp_001", "nlp_004"],
        ),
        ResearchPaper(
            paper_id="nlp_003",
            title="Language Models are Unsupervised Multitask Learners",
            authors=["Radford, A.", "Wu, J.", "Child, R."],
            abstract="GPT-2 demonstrates that language models begin learning these tasks without any explicit supervision when trained on a new dataset.",
            year=2019,
            citations=26000,
            keywords=["GPT-2", "language generation", "unsupervised"],
            related_papers=["nlp_001", "nlp_005"],
        ),
        ResearchPaper(
            paper_id="nlp_004",
            title="RoBERTa: A Robustly Optimized BERT Pretraining Approach",
            authors=["Liu, Y.", "Ott, M.", "Goyal, N."],
            abstract="We present RoBERTa, an optimized method for pretraining self-supervised language models with key training procedure modifications.",
            year=2019,
            citations=15000,
            keywords=["RoBERTa", "BERT", "optimization"],
            related_papers=["nlp_002", "nlp_001"],
        ),
        ResearchPaper(
            paper_id="nlp_005",
            title="GPT-3: Language Models are Few-Shot Learners",
            authors=["Brown, T.", "Mann, B.", "Ryder, N."],
            abstract="Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a diverse corpus and fine-tuning on a specific task.",
            year=2020,
            citations=35000,
            keywords=["GPT-3", "few-shot learning", "language model"],
            related_papers=["nlp_003", "nlp_001"],
        ),
    ]

    # Sample research papers - Computer Vision Focus
    cv_papers = [
        ResearchPaper(
            paper_id="cv_001",
            title="An Image is Worth 16x16 Words: Transformers for Image Recognition",
            authors=["Dosovitskiy, A.", "Beyer, L.", "Kolesnikov, A."],
            abstract="While the Transformer architecture has become the de-facto standard for natural language processing, its applications to computer vision remain limited. We show that a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks.",
            year=2020,
            citations=22000,
            keywords=["vision transformer", "image classification", "transformer"],
            related_papers=["cv_002", "cv_003"],
        ),
        ResearchPaper(
            paper_id="cv_002",
            title="Swin Transformer: Hierarchical Vision Transformer using Shifted Windows",
            authors=["Liu, Z.", "Lin, Y.", "Cao, Y."],
            abstract="A novel vision transformer, called Swin Transformer, that capably serves as a general-purpose backbone for computer vision. Swin Transformer is constructed by replacing the standard multi-head self attention module in each Transformer block with a shifted window based attention module.",
            year=2021,
            citations=15000,
            keywords=["Swin", "hierarchical", "vision"],
            related_papers=["cv_001", "cv_004"],
        ),
        ResearchPaper(
            paper_id="cv_003",
            title="Masked Autoencoders Are Scalable Vision Learners",
            authors=["He, K.", "Chen, X.", "Xie, S."],
            abstract="This paper shows that masked autoencoders (MAE) are scalable self-supervised learners for computer vision. Our MAE approach is simple: we mask random patches of the input image and reconstruct the missing pixels.",
            year=2021,
            citations=8000,
            keywords=["self-supervised", "vision", "masking"],
            related_papers=["cv_001", "cv_005"],
        ),
        ResearchPaper(
            paper_id="cv_004",
            title="DeiT: Data-efficient image Transformers",
            authors=["Touvron, H.", "Cord, M.", "Douze, M."],
            abstract="Recent advances in image classification both in academia and industry have been driven by Transformer models adapted from NLP. However, these visual transformers are computationally intensive and require significantly more data to reach high accuracy when compared to convolutional neural networks.",
            year=2020,
            citations=10000,
            keywords=["DeiT", "efficient", "data-efficient"],
            related_papers=["cv_001", "cv_002"],
        ),
        ResearchPaper(
            paper_id="cv_005",
            title="DINO: Emerging Properties in Self-Supervised Vision Transformers",
            authors=["Caron, M.", "Touvron, H.", "Misra, I."],
            abstract="We investigate the emerging self-supervised properties of vision transformers, and observe that they contain explicit semantic information about image regions and classes. We propose DINO, a method based on self-supervised learning with knowledge distillation without labels.",
            year=2021,
            citations=6000,
            keywords=["DINO", "self-supervised", "distillation"],
            related_papers=["cv_001", "cv_003"],
        ),
    ]

    all_papers = nlp_papers + cv_papers

    print("\n📚 Loading Research Papers:")
    print("\n   📝 NLP Research Track:")
    for paper in nlp_papers:
        print(f"      [{paper.paper_id}] {paper.title} ({paper.year})")

    print("\n   🖼️  Computer Vision Track:")
    for paper in cv_papers:
        print(f"      [{paper.paper_id}] {paper.title} ({paper.year})")

    # Initialize OMem
    print("\n🔧 Initializing paper library...")
    from ontomem.merger import MergeStrategy
    
    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS

        embedder = OpenAIEmbeddings(model="text-embedding-3-small")
        print("   ✅ OpenAI API key found - vector search enabled")

        library = OMem(
            memory_schema=ResearchPaper,
            key_extractor=lambda x: x.paper_id,
            llm_client=None,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )
    except Exception as e:
        print(f"   ⚠️  OpenAI not available - using keyword-only search")
        library = OMem(
            memory_schema=ResearchPaper,
            key_extractor=lambda x: x.paper_id,
            llm_client=None,
            embedder=None,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )

    # Add papers to library
    print("\n📖 Adding papers to unified research library...")
    library.add(all_papers)
    print(f"   Total papers in library: {library.size}")
    print(f"      • NLP papers: {len(nlp_papers)}")
    print(f"      • Computer Vision papers: {len(cv_papers)}")

    # Retrieve by ID from both tracks
    print("\n🔍 Direct Lookup (Papers from Both Tracks):")
    sample_papers = ["nlp_001", "cv_001"]
    for paper_id in sample_papers:
        paper = library.get(paper_id)
        if paper:
            track = "NLP" if paper_id.startswith("nlp") else "Computer Vision"
            print(f"\n   [{track}] {paper.title}")
            print(f"      Abstract: {paper.abstract[:80]}...")
            print(f"      Citations: {paper.citations:,}")

    # Demonstrate semantic search (if embeddings available)
    print("\n🎯 Semantic Search Examples:")
    print("-" * 80)

    search_queries = [
        "transformer neural networks",
        "vision image recognition",
        "self-supervised learning",
    ]

    for query in search_queries:
        print(f"\n   Query: '{query}'")
        try:
            # Attempt semantic search
            results = library.search(query, k=2)
            if results:
                print("   Results (by semantic similarity):")
                for i, paper_result in enumerate(results, 1):
                    print(f"      {i}. {paper_result.title}")
                    print(f"         Track: {'NLP' if paper_result.paper_id.startswith('nlp') else 'Computer Vision'}")
            else:
                print("   (Semantic search requires OpenAI API key)")
        except Exception:
            # Fallback: keyword search
            matching = [
                p
                for p in all_papers
                if any(kw.lower() in query.lower() for kw in p.keywords)
            ]
            if matching:
                print("   Results (by keyword match):")
                for i, p in enumerate(matching[:2], 1):
                    print(f"      {i}. {p.title}")

    # Persist library to disk
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    library_folder = temp_dir / "scholar_library"

    print(f"\n💾 Saving library to {library_folder.relative_to(temp_dir.parent)}...")
    library.dump(str(library_folder))
    print("   ✅ Library persisted")

    # Statistics
    print("\n📊 Library Statistics:")
    print("-" * 80)
    total_citations = sum(p.citations for p in all_papers)
    avg_year = sum(p.year for p in all_papers) / len(all_papers)
    all_keywords = set()
    for p in all_papers:
        all_keywords.update(p.keywords)

    print(f"   Total Papers: {len(all_papers)}")
    print(f"      • NLP Research: {len(nlp_papers)} papers ({sum(p.citations for p in nlp_papers):,} citations)")
    print(f"      • Computer Vision: {len(cv_papers)} papers ({sum(p.citations for p in cv_papers):,} citations)")
    print(f"\n   Total Citations: {total_citations:,}")
    print(f"   Average Publication Year: {avg_year:.0f}")
    print(f"   Unique Keywords: {len(all_keywords)}")
    print(f"   Most Cited Paper: {max(all_papers, key=lambda p: p.citations).title}")

    # Show top keywords
    keyword_freq = {}
    for p in all_papers:
        for kw in p.keywords:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

    print(f"\n   Top Keywords (across all tracks):")
    for kw, freq in sorted(keyword_freq.items(), key=lambda x: -x[1])[:5]:
        print(f"      • {kw}: {freq} papers")

    print("\n" + "=" * 80)
    print("✨ Research paper library ready for exploration!")
    print("=" * 80)


if __name__ == "__main__":
    example_semantic_scholar()
