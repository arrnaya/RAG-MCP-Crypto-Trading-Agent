import streamlit as st
from rag_pipeline import query
from model_context import ConversationMemory
from loguru import logger
import uuid

st.set_page_config(page_title="Crypto RAG Agent", layout="wide")
st.title("💹 Crypto Trading Expert Agent")

# Initialize session state for conversation memory
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

query_input = st.text_input("Enter your question about crypto trading")
if query_input:
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    with st.spinner("Thinking like a pro trader..."):
        logger.info(f"UI query: {query_input} [CID: {correlation_id}]")
        response = query(query_input)
        st.session_state.memory.update(query_input, response)
        st.markdown(f"**💬 Response:**\n\n{response}")
        st.markdown("**📜 Conversation History:**")
        st.text(st.session_state.memory.get_context())