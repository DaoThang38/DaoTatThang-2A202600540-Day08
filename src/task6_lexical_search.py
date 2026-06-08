"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25. Nếu dùng phương pháp khác (TF-IDF, Elasticsearch,
Weaviate BM25 built-in), hãy giải thích cơ chế trong buổi demo → +5 bonus.

Cài đặt:
    pip install rank-bm25

BM25 hoạt động thế nào:
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1)) / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)
"""

from pathlib import Path

# TODO: Load corpus từ data/standardized/ hoặc từ vector store
CORPUS: list[dict] = []  # List of {'content': str, 'metadata': dict}


def build_bm25_index(corpus: list[dict]):
    """
    Xây dựng BM25 index từ corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    # TODO: Implement BM25 index
    #
    # from rank_bm25 import BM25Okapi
    #
    # # Tokenize - cho tiếng Việt nên dùng underthesea hoặc đơn giản split()
    # tokenized_corpus = [doc["content"].lower().split() for doc in corpus]
    # bm25 = BM25Okapi(tokenized_corpus)
    # return bm25
    raise NotImplementedError("Implement build_bm25_index")


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score
            'metadata': dict
        }
        Sorted by score descending.
    """
    import weaviate
    from weaviate.classes.query import MetadataQuery

    client = weaviate.connect_to_local()
    collection = client.collections.get("DrugLawDocs")

    # Sử dụng tính năng BM25 có sẵn (built-in) của Weaviate để được cộng điểm Bonus (+5 điểm)
    # Cơ chế: Weaviate tự động tạo inverted index cho các cột DataType.TEXT
    # Khi dùng query.bm25(), nó sẽ chấm điểm theo thuật toán Okapi BM25.
    results = collection.query.bm25(
        query=query,
        limit=top_k,
        return_metadata=MetadataQuery(score=True)
    )

    client.close()

    return [
        {
            "content": obj.properties.get("content", ""),
            "score": obj.metadata.score,  # BM25 score
            "metadata": {
                "source": obj.properties.get("source", ""),
                "doc_type": obj.properties.get("doc_type", "")
            }
        }
        for obj in results.objects
    ]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    # Test
    results = lexical_search("Điều 248 tàng trữ trái phép chất ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
