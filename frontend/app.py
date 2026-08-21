import os
import streamlit as st
import requests

st.set_page_config(page_title="iMessage Memory AI", page_icon="💬", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .chat-bubble { padding: 12px 16px; border-radius: 12px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("💬 iMessage Memory Assistant")
st.caption("Ask anything about your past conversations, memories, places, or events.")

try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("🔍 View Retrieved Source Memories"):
                for idx, src in enumerate(msg["sources"], 1):
                    st.caption(f"**Source {idx}:**")
                    st.text(src)

if user_query := st.chat_input("Ask about a memory..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching chat vault..."):
            try:
                res = requests.post(f"{API_URL}/api/chat", json={"message": user_query}, timeout=60)
                if res.status_code == 200:
                    data = res.json()
                    answer = data["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": data.get("sources", []),
                    })
                else:
                    st.error("Error communicating with backend API server.")
            except Exception as e:
                st.error(f"Failed to connect to backend server: {e}")
