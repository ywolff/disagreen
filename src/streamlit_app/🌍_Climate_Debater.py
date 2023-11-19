"""Home page of the Streamlit app."""
import json
import time

import openai
import streamlit as st

from src.streamlit_app.utils.set_page_config import set_page_config

ASSISTANT_ID = "asst_HRcxWWtlex8F5rf8rrDRx9tK"


def get_response(
    client: openai.OpenAI,
    prompt: str,
) -> None:
    """Get response from assistant, update session state, and rerun app."""
    client.beta.threads.messages.create(
        thread_id=st.session_state["thread"].id,
        role="user",
        content=prompt,
    )
    st.session_state["run"] = client.beta.threads.runs.create(
        thread_id=st.session_state["thread"].id,
        assistant_id=ASSISTANT_ID,
    )
    completed = False
    while not completed:
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state["thread"].id,
            run_id=st.session_state["run"].id,
        )
        if run.status == "completed":
            completed = True
        else:
            time.sleep(0.1)
    thread_messages = client.beta.threads.messages.list(
        thread_id=st.session_state["thread"].id
    ).data
    st.session_state["messages"] = [
        {
            "content": json.loads(thread_message.content[0].text.value)["response"]
            if thread_message.role == "assistant"
            else thread_message.content[0].text.value,
            "role": thread_message.role,
        }
        for thread_message in thread_messages
    ]
    st.session_state["is_convinced"] = json.loads(
        thread_messages[0].content[0].text.value
    )["is_convinced"]
    st.rerun()


def main() -> None:
    """Home page of the Streamlit app."""
    set_page_config()
    st.title("Welcome to Climate Debater")

    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "is_convinced" not in st.session_state:
        st.session_state["is_convinced"] = False
    if "thread" not in st.session_state:
        st.session_state["thread"] = client.beta.threads.create()
        get_response(client, prompt="Que penses-tu du dérèglement climatique ?")

    if st.session_state["is_convinced"]:
        st.success("The debater is convinced!")
    else:
        st.error("The debater is not yet convinced!")

    for message in reversed(st.session_state["messages"]):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Votre réponse"):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.text("...")
        get_response(client, prompt=prompt)


if __name__ == "__main__":
    main()
