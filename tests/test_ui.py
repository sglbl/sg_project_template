"""Unit test for UI presentation initialization."""

from src.presentation.ui.sidebar import fetch_api_items, check_postgres_connection
from src.presentation.ui.assets import get_logo_html


def test_ui_helpers() -> None:
    """Ensure Streamlit UI asset and sidebar helpers function properly."""
    logo_html = get_logo_html("", "")
    assert isinstance(logo_html, str)

    success, _ = fetch_api_items(api_url="http://localhost:99999")
    assert success is False

    success_db, _ = check_postgres_connection()
    assert isinstance(success_db, bool)
