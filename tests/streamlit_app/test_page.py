"""Test that each Streamlit page can be run."""
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from src.constants.paths import PROJECT_ROOT_PATH

STREAMLIT_APP_PATH = PROJECT_ROOT_PATH / "src" / "streamlit_app"
STREAMLIT_PAGE_PATH = STREAMLIT_APP_PATH / "🌍_Disagreen.py"


@patch("openai.OpenAI")
def test_streamlit_page(openai_mock) -> None:
    openai_mock().beta.threads.runs.retrieve().status = "completed"
    openai_mock().beta.threads.messages.list().data[0].role = "assistant"
    openai_mock().beta.threads.messages.list().data[0].content[
        0
    ].text.value = '{"response": "response", "is_convinced": true}'

    app_test = AppTest.from_file(str(STREAMLIT_PAGE_PATH))
    app_test.secrets["OPENAI_API_KEY"] = "API_KEY"
    app_test.run()

    assert not app_test.exception
    openai_mock.assert_called_with(api_key="API_KEY")
