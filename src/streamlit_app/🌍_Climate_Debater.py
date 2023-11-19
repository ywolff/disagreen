"""Home page of the Streamlit app."""
import json
import pathlib
import sys
import time

import openai
import streamlit as st

sys.path.append(str(pathlib.Path(__file__).parents[2].absolute()))

from src.streamlit_app.utils.set_page_config import set_page_config

ASSISTANT_ID = "asst_PgZZtxItYNNAo0UINFliTvCw"


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
            "content": ""
            if not hasattr(thread_message.content[0], "text")
            else json.loads(thread_message.content[0].text.value)["response"]
            if thread_message.role == "assistant"
            else thread_message.content[0].text.value,
            "role": thread_message.role,
        }
        for thread_message in thread_messages
    ]
    if hasattr(thread_messages[0].content[0], "text"):
        st.session_state["is_convinced"] = json.loads(
            thread_messages[0].content[0].text.value
        )["is_convinced"]
    st.rerun()


def main() -> None:
    """Home page of the Streamlit app."""
    set_page_config()
    st.header("Convaincs ton interlocuteur qu'il faut agir pour le climat !")

    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "is_convinced" not in st.session_state:
        st.session_state["is_convinced"] = False
    if "thread" not in st.session_state:
        st.session_state["thread"] = client.beta.threads.create()
        with st.spinner("Chargement..."):
            get_response(
                client,
                prompt="Penses tu qu'il faut agir davantage pour lutter contre le dérèglement climatique ?",
            )

    for message in reversed(st.session_state["messages"]):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ta réponse"):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.text("...")
        get_response(client, prompt=prompt)

    if st.session_state["is_convinced"]:
        st.success("Tu as convaincu ton interlocuteur, bravo !")
    else:
        st.error("Ton interlocuteur ne semble pas encore convaincu...")


if __name__ == "__main__":
    main()
