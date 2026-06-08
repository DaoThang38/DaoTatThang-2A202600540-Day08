"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    import weaviate
    from weaviate.classes.query import MetadataQuery
    from sentence_transformers import SentenceTransformer

    # Khởi tạo model một lần duy nhất (caching) để tránh OOM GPU
    global _semantic_model
    if "_semantic_model" not in globals():
        _semantic_model = SentenceTransformer("BAAI/bge-m3")

    # Bước 1: Embed query bằng cùng model ở Task 4
    query_embedding = _semantic_model.encode(query, show_progress_bar=False).tolist()

    # Bước 2: Query vector store (cosine similarity)
    client = weaviate.connect_to_local()
    collection = client.collections.get("DrugLawDocs")

    results = collection.query.near_vector(
        near_vector=query_embedding,
        limit=top_k,
        return_metadata=MetadataQuery(distance=True)
    )

    client.close()

    # Bước 3: Return top_k results
    return [
        {
            "content": obj.properties.get("content", ""),
            "score": 1 - (obj.metadata.distance or 0),  # distance → similarity
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
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
