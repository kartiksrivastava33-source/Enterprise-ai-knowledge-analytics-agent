
import streamlit as st
import requests

st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("Enterprise AI Knowledge & Analytics Agent")
st.caption("Ask questions about business documents and sales data.")

API_URL = "http://backend:8000/ask"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit_user_01"


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input("Ask a question...")

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:
                response = requests.post(
                    API_URL,
                    json={
                        "question": question,
                        "thread_id": st.session_state.thread_id
                    },
                    timeout=120
                )

                response.raise_for_status()
                result = response.json()

                answer = result["answer"]

                st.markdown(answer)

                if result.get("sources"):
                    st.markdown("**Sources**")
                    for source in result["sources"]:
                        st.write(f"- {source}")

                if result.get("insights"):
                    st.markdown("**Insights**")
                    for insight in result["insights"]:
                        st.write(f"- {insight}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.RequestException as e:
                st.error(f"API connection failed: {e}")
