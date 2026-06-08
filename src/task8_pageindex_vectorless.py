"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/
SDK & sample code: https://github.com/VectifyAI/PageIndex

PageIndex cho phép RAG mà không cần vector store — sử dụng
structural understanding của document thay vì embedding.

Cài đặt:
    pip install pageindex

Hướng dẫn:
    1. Đăng ký account tại pageindex.ai
    2. Lấy API key
    3. Upload documents
    4. Query sử dụng PageIndex API
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "d04793582f90468f8eb86022c6a9d293")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents():
    """
    Upload toàn bộ tài liệu PDF lên PageIndex (API mới yêu cầu PDF thay vì Markdown).
    """
    from pageindex import PageIndexClient

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    
    pdf_dir = Path(__file__).parent.parent / "data" / "landing" / "legal"
    for pdf_file in pdf_dir.rglob("*.pdf"):
        try:
            res = client.submit_document(file_path=str(pdf_file))
            doc_id = res.get("doc_id", "unknown")
            print(f"  ✓ Uploaded: {pdf_file.name} (ID: {doc_id})")
        except Exception as e:
            print(f"  ✗ Lỗi upload {pdf_file.name}: {e}")

def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex.
    """
    from pageindex import PageIndexClient
    import time

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    
    # Demo: Tìm kiếm trên tài liệu đầu tiên trong kho
    docs = client.list_documents()
    doc_list = docs.get('documents', [])
    if not doc_list:
        print("Chưa có tài liệu nào trên PageIndex!")
        return []
        
    doc_id = doc_list[0]['id']
    
    try:
        # Submit query
        res = client.submit_query(doc_id=doc_id, query=query)
        retrieval_id = res.get("retrieval_id")
        
        # Đợi xử lý (Polling)
        for _ in range(3):
            time.sleep(2)
            ret = client.get_retrieval(retrieval_id)
            if ret.get("status") == "completed":
                break
                
        # Trả về kết quả (do API thay đổi liên tục, giả lập kết cấu trả về)
        return [
            {
                "content": str(ret),
                "score": 1.0,
                "metadata": {"doc_id": doc_id},
                "source": "pageindex"
            }
        ]
    except Exception as e:
        print(f"Lỗi khi search qua PageIndex: {e}")
        return []


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    if not PAGEINDEX_API_KEY:
        print("⚠ Hãy set PAGEINDEX_API_KEY trong file .env")
        print("  Đăng ký tại: https://pageindex.ai/")
    else:
        print("Uploading documents...")
        upload_documents()

        print("\nTest query:")
        results = pageindex_search("hình phạt sử dụng ma tuý", top_k=3)
        for r in results:
            print(f"[{r['score']:.3f}] {r['content'][:100]}...")
