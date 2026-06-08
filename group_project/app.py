"""
RAG Chatbot — Streamlit UI
Pháp luật Ma Tuý & Tin Tức Nghệ Sĩ

Chạy:
    streamlit run group_project/app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Thêm root vào path để import src
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Chatbot – Ma Tuý & Pháp Luật",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Header */
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-sub {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

/* Chat messages */
.chat-user {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 8px 0;
    margin-left: 15%;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
}
.chat-bot {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    margin: 8px 0;
    margin-right: 15%;
    color: #e2e8f0;
    backdrop-filter: blur(10px);
}
.source-badge {
    display: inline-block;
    background: rgba(99, 102, 241, 0.2);
    border: 1px solid rgba(99, 102, 241, 0.4);
    color: #a5b4fc;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.78rem;
    margin: 2px 3px;
}
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    backdrop-filter: blur(10px);
}
.metric-num {
    font-size: 1.8rem;
    font-weight: 700;
    color: #a78bfa;
}
.metric-label {
    font-size: 0.8rem;
    color: #94a3b8;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.9);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Input */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: white !important;
    border-radius: 12px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4);
}

/* Expander */
.streamlit-expanderHeader {
    color: #a5b4fc !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Load RAG pipeline (cached)
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Đang khởi tạo RAG pipeline...")
def load_pipeline():
    from src.task9_retrieval_pipeline import retrieve
    from src.task10_generation import generate_with_citation
    return retrieve, generate_with_citation


def ask(question: str, history: list) -> dict:
    """Gọi pipeline và trả về kết quả."""
    retrieve, generate_with_citation = load_pipeline()

    # Tích hợp conversation history vào câu hỏi (simple memory)
    if history:
        context_turns = history[-4:]  # Giữ 2 lượt gần nhất
        history_text = "\n".join(
            f"Người dùng: {t['q']}\nTrợ lý: {t['a'][:200]}..."
            for t in context_turns
        )
        augmented_q = f"[Lịch sử hội thoại]\n{history_text}\n\n[Câu hỏi mới]: {question}"
    else:
        augmented_q = question

    chunks = retrieve(augmented_q)
    result = generate_with_citation(question, chunks)  # generation dùng câu hỏi gốc
    return result


# ─────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ RAG Chatbot")
    st.markdown("Hỏi đáp về **Pháp luật Ma Tuý** và **Tin tức Nghệ sĩ**")
    st.divider()

    # Stats
    st.markdown("### 📊 Thống kê")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-num">{st.session_state.total_queries}</div>
            <div class="metric-label">Câu hỏi</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-num">{len(st.session_state.messages) // 2}</div>
            <div class="metric-label">Lượt chat</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Gợi ý câu hỏi
    st.markdown("### 💡 Câu hỏi gợi ý")
    sample_questions = [
        "Ca sĩ Chi Dân bị bắt vì tội gì?",
        "Hình phạt tàng trữ ma túy theo Điều 249?",
        "Hữu Tín bị kết án bao nhiêu năm?",
        "Quy trình cai nghiện bắt buộc gồm mấy bước?",
        "Những nghệ sĩ nào bị bắt vì ma túy?",
        "Châu Việt Cường bị phạt tù bao lâu?",
    ]
    for q in sample_questions:
        if st.button(f"💬 {q}", key=f"btn_{q}", use_container_width=True):
            st.session_state["prefill_q"] = q

    st.divider()

    # Clear chat
    if st.button("🗑️ Xoá lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.total_queries = 0
        st.rerun()

    st.markdown("""
    <div style="color:#64748b; font-size:0.75rem; margin-top:1rem; text-align:center">
    Powered by Gemini Flash + Weaviate<br>
    BAAI/bge-m3 Embeddings
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Main content
# ─────────────────────────────────────────────
st.markdown('<div class="hero-title">⚖️ Trợ lý Pháp luật Ma Tuý</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Hệ thống RAG hỏi đáp về pháp luật phòng chống ma tuý và tin tức liên quan</div>', unsafe_allow_html=True)

# Hiển thị chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">🙋 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            # Bot message
            st.markdown(f'<div class="chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
            # Sources
            if msg.get("sources"):
                with st.expander(f"📚 Nguồn tham khảo ({len(msg['sources'])} chunks)", expanded=False):
                    for i, src in enumerate(msg["sources"], 1):
                        src_name = src.get("source", f"chunk_{i}")
                        score = src.get("score", "")
                        score_str = f" | score: {score:.3f}" if score else ""
                        st.markdown(f"**[{i}] {src_name}**{score_str}")
                        st.markdown(f"> {src.get('content', '')[:300]}...")
                        st.divider()

# Input
st.markdown("---")
prefill = st.session_state.pop("prefill_q", "")

with st.form("chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Nhập câu hỏi của bạn...",
            value=prefill,
            placeholder="Ví dụ: Ca sĩ Chi Dân bị bắt vì tội gì?",
            label_visibility="collapsed",
        )
    with col_btn:
        submitted = st.form_submit_button("Gửi ➤", use_container_width=True)

if submitted and user_input.strip():
    question = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.total_queries += 1

    with st.spinner("Đang tìm kiếm và tổng hợp câu trả lời..."):
        try:
            result = ask(question, st.session_state.history)
            answer = result.get("answer", "Không thể trả lời.")
            sources = result.get("sources", [])

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })
            st.session_state.history.append({"q": question, "a": answer})

            # Giữ history tối đa 10 lượt
            if len(st.session_state.history) > 10:
                st.session_state.history = st.session_state.history[-10:]

        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Lỗi: {e}",
                "sources": [],
            })

    st.rerun()
