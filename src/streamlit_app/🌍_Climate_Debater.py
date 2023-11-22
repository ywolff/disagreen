"""Home page of the Streamlit app."""
import json
import sys
import time
from pathlib import Path

import openai
import streamlit as st
import yaml

# Needed to make absolute imports from `src` work on Streamlit Cloud
sys.path.append(str(Path(__file__).parents[2].absolute()))

from src.constants.paths import ASSISTANTS_IDS_YAML_PATH  # noqa E402
from src.streamlit_app.utils.set_page_config import set_page_config  # noqa E402

INITIAL_PROMPT = (
    "Penses tu qu'il faut agir davantage pour lutter contre le dérèglement climatique ?"
)
# TODO: Avoid coupling with `assistants_config.py`
DEBATER_NAMES = ["Martine", "Sophie", "Francis"]


def main() -> None:
    """Home page of the Streamlit app."""
    set_page_config()

    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "assistants_ids" not in st.session_state:
        with open(ASSISTANTS_IDS_YAML_PATH) as assistants_ids_yaml:
            st.session_state["assistants_ids"] = yaml.safe_load(assistants_ids_yaml)
    if "current_level" not in st.session_state:
        st.session_state["current_level"] = 0
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "is_convinced" not in st.session_state:
        st.session_state["is_convinced"] = False

    col_1, col_2 = st.columns([1, 3])
    with col_1:
        st.subheader("🌍 Climate Debater")
    with col_2:
        st.progress(
            value=st.session_state["current_level"]
            / len(st.session_state["assistants_ids"]),
            text=f"Niveau {st.session_state['current_level'] + 1}",
        )
    st.info(
        f"Convaincs {DEBATER_NAMES[st.session_state['current_level']]} qu'il faut agir pour le climat !",
    )
    st.divider()

    if "thread" not in st.session_state:
        st.session_state["thread"] = client.beta.threads.create()
        with st.spinner("Chargement..."):
            get_response(
                client,
                prompt=INITIAL_PROMPT,
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
        st.success(
            f"Tu as convaincu {DEBATER_NAMES[st.session_state['current_level']]}, bravo !",
            icon="🍀",
        )
        if (
            st.session_state["current_level"]
            == len(st.session_state["assistants_ids"]) - 1
        ):
            st.success("Tu as terminé tous les niveaux, félicitations !", icon="🎉")
        elif st.button("Niveau suivant"):
            st.session_state["current_level"] += 1
            st.session_state["messages"] = []
            st.session_state["is_convinced"] = False
            del st.session_state["thread"]
            st.rerun()

        st.balloons()


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
        assistant_id=st.session_state["assistants_ids"][
            st.session_state["current_level"]
        ],
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


if __name__ == "__main__":
    main()
