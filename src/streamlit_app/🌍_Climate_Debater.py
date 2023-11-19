"""Home page of the Streamlit app."""

from typing import TypedDict

import numpy as np
import streamlit as st
from openai import OpenAI

from src.streamlit_app.utils.set_page_config import set_page_config


class DebaterResponse(TypedDict):
    """Response from the debater AI."""

    response: str
    is_convinced: bool


def dummy_get_response(
    client: OpenAI, messages: list[dict[str, str]]
) -> DebaterResponse:
    """Dummy response from the debater AI."""
    return {
        "response": "I think that we should use more solar energy.",
        "is_convinced": np.random.choice([True, False]),
    }


def main() -> None:
    """Home page of the Streamlit app."""
    set_page_config()
    st.title("Welcome to Climate Debater")

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_convinced" not in st.session_state:
        st.session_state.is_convinced = False

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            debater_response = dummy_get_response(
                client,
                [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )
            message_placeholder.markdown(debater_response["response"])

        st.session_state.messages.append(
            {"role": "assistant", "content": debater_response["response"]}
        )
        st.session_state.is_convinced = debater_response["is_convinced"]

    if st.session_state.is_convinced:
        st.success("The debater is convinced!")
    else:
        st.error("The debater is not convinced!")


if __name__ == "__main__":
    main()
