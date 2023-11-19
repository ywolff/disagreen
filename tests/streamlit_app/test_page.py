"""Test that each Streamlit page can be run."""
from streamlit.testing.v1 import AppTest

from src.constants import PROJECT_ROOT_PATH

STREAMLIT_APP_PATH = PROJECT_ROOT_PATH / "src" / "streamlit_app"
STREAMLIT_PAGE_PATH = STREAMLIT_APP_PATH / "🌍_Climate_Debater.py"


def test_streamlit_page() -> None:
    app_test = AppTest.from_file(str(STREAMLIT_PAGE_PATH))
    app_test.run()

    assert not app_test.exception
