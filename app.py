import streamlit as st

from src.agent import SupportAgent
from src.llm.gemini import GeminiClient
from src.retrieval.retriever import Retriever


st.set_page_config(
    page_title="Aster & Row Support Agent",
    page_icon="🤖"
)


@st.cache_resource
def create_agent():

    retriever = Retriever()
    llm = GeminiClient()

    return SupportAgent(
        llm=llm,
        retriever=retriever
    )


st.title("Aster & Row Support Agent")

st.caption(
    "Reliable RAG customer-support agent — "
    "authority-aware retrieval, sanitized order lookups, "
    "and explicit conflict detection."
)

try:
    if "agent" not in st.session_state:
        st.session_state.agent = create_agent()
except RuntimeError as e:
    st.error(str(e))
    st.stop()


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_message = st.chat_input(
    "Ask about returns, shipping, or an order..."
)


if user_message:

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.respond(user_message)
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
