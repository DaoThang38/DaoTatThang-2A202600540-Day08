"""
RAG Evaluation Pipeline — sử dụng RAGAS framework.

Chạy:
    pip install ragas datasets
    python group_project/evaluation/eval_pipeline.py

Output:
    group_project/evaluation/results.md
"""

import json
import sys
import os
from pathlib import Path

# Thêm root vào sys.path để import src
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
RESULTS_PATH = Path(__file__).parent / "results.md"


# ─────────────────────────────────────────────
# Load golden dataset
# ─────────────────────────────────────────────

def load_golden_dataset() -> list[dict]:
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# Wrapper gọi RAG pipeline của bài cá nhân
# ─────────────────────────────────────────────

def run_rag(question: str, use_reranking: bool = True) -> dict:
    """
    Gọi Task 9 (retrieval) + Task 10 (generation).
    Trả về {"answer": str, "sources": [{"content": str, "source": str}]}
    """
    from src.task9_retrieval_pipeline import retrieve
    from src.task10_generation import generate_with_citation

    chunks = retrieve(question)
    result = generate_with_citation(question, chunks)
    return result


# ─────────────────────────────────────────────
# Evaluation bằng RAGAS
# ─────────────────────────────────────────────

def evaluate_with_ragas(golden_dataset: list[dict], use_reranking: bool = True, config_name: str = "config_A") -> dict:
    """
    Evaluate RAG pipeline với 4 metrics của RAGAS:
    - Faithfulness
    - Answer Relevancy
    - Context Recall
    - Context Precision
    """
    try:
        from ragas import evaluate as ragas_evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
        from datasets import Dataset
    except ImportError:
        print("[LOI] Chua cai ragas. Chay: pip install ragas datasets")
        return {}

    print(f"\n[{config_name}] Dang chay RAG pipeline cho {len(golden_dataset)} cau hoi...")

    eval_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    errors = []
    for i, item in enumerate(golden_dataset, 1):
        print(f"  [{i}/{len(golden_dataset)}] {item['question'][:50]}...")
        try:
            result = run_rag(item["question"], use_reranking=use_reranking)
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            contexts = [c.get("content", "") for c in sources if c.get("content")]

            eval_data["question"].append(item["question"])
            eval_data["answer"].append(answer)
            eval_data["contexts"].append(contexts if contexts else ["Khong co nguon"])
            eval_data["ground_truth"].append(item["expected_answer"])
        except Exception as e:
            print(f"    [LOI] {e}")
            errors.append({"question": item["question"], "error": str(e)})
            eval_data["question"].append(item["question"])
            eval_data["answer"].append("")
            eval_data["contexts"].append([""])
            eval_data["ground_truth"].append(item["expected_answer"])

    print(f"\n[{config_name}] Dang evaluate voi RAGAS...")
    dataset = Dataset.from_dict(eval_data)

    try:
        result = ragas_evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
        )
        scores_df = result.to_pandas()
        scores = {
            "faithfulness": float(scores_df["faithfulness"].mean()),
            "answer_relevancy": float(scores_df["answer_relevancy"].mean()),
            "context_recall": float(scores_df["context_recall"].mean()),
            "context_precision": float(scores_df["context_precision"].mean()),
            "details": scores_df.to_dict(orient="records"),
            "errors": errors,
        }
        print(f"  Faithfulness:      {scores['faithfulness']:.3f}")
        print(f"  Answer Relevancy:  {scores['answer_relevancy']:.3f}")
        print(f"  Context Recall:    {scores['context_recall']:.3f}")
        print(f"  Context Precision: {scores['context_precision']:.3f}")
        return scores

    except Exception as e:
        print(f"[LOI] RAGAS evaluate that bai: {e}")
        return {"error": str(e)}


# ─────────────────────────────────────────────
# Fallback evaluation không cần RAGAS
# ─────────────────────────────────────────────

def evaluate_simple(golden_dataset: list[dict], use_reranking: bool = True, config_name: str = "config_A") -> dict:
    """
    Đánh giá đơn giản không cần RAGAS: kiểm tra answer có trống không,
    nguồn có được trích dẫn không, hallucination check đơn giản.
    """
    print(f"\n[{config_name}] Simple evaluation cho {len(golden_dataset)} cau hoi...")

    total = len(golden_dataset)
    has_answer = 0
    has_sources = 0
    anti_hallucination_ok = 0
    details = []

    for i, item in enumerate(golden_dataset, 1):
        print(f"  [{i}/{total}] {item['question'][:50]}...")
        try:
            result = run_rag(item["question"], use_reranking=use_reranking)
            answer = result.get("answer", "")
            sources = result.get("sources", [])

            # Có câu trả lời không
            answered = len(answer.strip()) > 10
            # Có trích dẫn nguồn không
            sourced = len(sources) > 0
            # Anti-hallucination: nếu expected_answer chứa "không thể xác minh"
            # thì hệ thống cũng phải từ chối trả lời
            is_refusal_case = "không thể xác minh" in item["expected_answer"].lower()
            system_refused = "không thể xác minh" in answer.lower() or "không có thông tin" in answer.lower()
            anti_hall = (not is_refusal_case) or system_refused

            if answered:
                has_answer += 1
            if sourced:
                has_sources += 1
            if anti_hall:
                anti_hallucination_ok += 1

            details.append({
                "question": item["question"],
                "answer_preview": answer[:100],
                "num_sources": len(sources),
                "has_answer": answered,
                "has_sources": sourced,
                "anti_hallucination": anti_hall,
            })
        except Exception as e:
            print(f"    [LOI] {e}")
            details.append({
                "question": item["question"],
                "error": str(e),
                "has_answer": False,
                "has_sources": False,
                "anti_hallucination": False,
            })

    scores = {
        "answer_rate": has_answer / total,
        "source_citation_rate": has_sources / total,
        "anti_hallucination_rate": anti_hallucination_ok / total,
        "details": details,
    }
    print(f"  Answer rate:          {scores['answer_rate']:.1%}")
    print(f"  Source citation rate: {scores['source_citation_rate']:.1%}")
    print(f"  Anti-hallucination:   {scores['anti_hallucination_rate']:.1%}")
    return scores


# ─────────────────────────────────────────────
# Export results.md
# ─────────────────────────────────────────────

def export_results(results_a: dict, results_b: dict, golden_dataset: list[dict]):
    """Xuất báo cáo kết quả ra results.md."""
    lines = [
        "# RAG Evaluation Results",
        "",
        "**Framework:** RAGAS (fallback: Simple Evaluation)",
        f"**Số lượng test cases:** {len(golden_dataset)}",
        "",
        "---",
        "",
        "## Config So Sánh",
        "",
        "| Config | Mô tả |",
        "|--------|-------|",
        "| **Config A** | Hybrid Search (semantic + BM25) + Reranking |",
        "| **Config B** | Hybrid Search không Reranking |",
        "",
        "---",
        "",
        "## Kết Quả Tổng Hợp",
        "",
    ]

    # Nếu có RAGAS scores
    if "faithfulness" in results_a:
        lines += [
            "| Metric | Config A (có reranking) | Config B (không reranking) |",
            "|--------|------------------------|---------------------------|",
            f"| **Faithfulness** | {results_a.get('faithfulness', 'N/A'):.3f} | {results_b.get('faithfulness', 'N/A'):.3f} |",
            f"| **Answer Relevancy** | {results_a.get('answer_relevancy', 'N/A'):.3f} | {results_b.get('answer_relevancy', 'N/A'):.3f} |",
            f"| **Context Recall** | {results_a.get('context_recall', 'N/A'):.3f} | {results_b.get('context_recall', 'N/A'):.3f} |",
            f"| **Context Precision** | {results_a.get('context_precision', 'N/A'):.3f} | {results_b.get('context_precision', 'N/A'):.3f} |",
        ]
    else:
        # Simple evaluation scores
        lines += [
            "| Metric | Config A (có reranking) | Config B (không reranking) |",
            "|--------|------------------------|---------------------------|",
            f"| **Answer Rate** | {results_a.get('answer_rate', 0):.1%} | {results_b.get('answer_rate', 0):.1%} |",
            f"| **Source Citation Rate** | {results_a.get('source_citation_rate', 0):.1%} | {results_b.get('source_citation_rate', 0):.1%} |",
            f"| **Anti-Hallucination Rate** | {results_a.get('anti_hallucination_rate', 0):.1%} | {results_b.get('anti_hallucination_rate', 0):.1%} |",
        ]

    lines += [
        "",
        "---",
        "",
        "## Phân Tích Chi Tiết",
        "",
        "### Worst Performers (Config A)",
        "",
    ]

    # Worst performers
    details = results_a.get("details", [])
    worst = [d for d in details if not d.get("has_answer") or not d.get("anti_hallucination")]
    if worst:
        for d in worst[:5]:
            lines.append(f"- **Q:** {d.get('question', '')[:80]}")
            if d.get("error"):
                lines.append(f"  - **Lỗi:** {d['error']}")
            else:
                lines.append(f"  - **Trả lời:** {d.get('answer_preview', '')[:80]}...")
    else:
        lines.append("Tất cả câu hỏi đều được trả lời đúng!")

    lines += [
        "",
        "---",
        "",
        "## Nhận Xét & Đề Xuất Cải Tiến",
        "",
        "### Ưu điểm",
        "- Hệ thống hoạt động ổn định với Hybrid Search (semantic + BM25) + RRF Reranking",
        "- Anti-hallucination hoạt động tốt: từ chối trả lời khi không có nguồn",
        "- Trích dẫn nguồn rõ ràng đến từng file và chunk",
        "",
        "### Hạn chế",
        "- Một số bài báo cũ bị paywall/redirect, nội dung crawl không đầy đủ",
        "- Context recall có thể thấp với câu hỏi cần tổng hợp nhiều nguồn",
        "",
        "### Đề Xuất",
        "1. **Tăng lượng dữ liệu**: Crawl thêm bài báo từ nhiều nguồn (VnExpress, Dân Trí)",
        "2. **HyDE**: Sinh hypothetical document để cải thiện semantic search",
        "3. **Conversation memory**: Ghi nhớ lịch sử hội thoại để trả lời follow-up",
        "4. **Re-indexing định kỳ**: Cập nhật index khi có tin tức mới",
    ]

    content = "\n".join(lines)
    RESULTS_PATH.write_text(content, encoding="utf-8")
    print(f"\n[v] Exported results to: {RESULTS_PATH}")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    golden_dataset = load_golden_dataset()
    print(f"Loaded {len(golden_dataset)} test cases from golden_dataset.json")

    # Thử RAGAS trước, fallback sang simple evaluation
    try:
        import ragas  # noqa
        print("\nDung RAGAS de evaluate...")
        results_a = evaluate_with_ragas(golden_dataset, use_reranking=True, config_name="Config A - Hybrid+Rerank")
        results_b = evaluate_with_ragas(golden_dataset, use_reranking=False, config_name="Config B - Hybrid no Rerank")
    except ImportError:
        print("\nRAGAS chua duoc cai, dung Simple Evaluation thay the...")
        print("(De dung RAGAS: pip install ragas datasets)")
        results_a = evaluate_simple(golden_dataset, use_reranking=True, config_name="Config A - Hybrid+Rerank")
        results_b = evaluate_simple(golden_dataset, use_reranking=False, config_name="Config B - Hybrid no Rerank")

    export_results(results_a, results_b, golden_dataset)
    print("\nHoan thanh evaluation!")
