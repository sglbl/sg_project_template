"""Streamlit sidebar presentation component for sg_project_template."""

import requests
import streamlit as st
from src.config import settings
from src.presentation.ui.assets import get_logo_html


def check_postgres_connection() -> tuple[bool, str]:
    """Helper to check Postgres database connection."""
    try:
        from sqlalchemy import text
        from src.infra.postgres.database_sync import get_db_sync
        with get_db_sync() as db:
            db.execute(text("SELECT 1;"))
        return True, f"Connected to Postgres ({settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME})"
    except Exception as e:
        return False, f"Postgres unavailable: {e}"


def fetch_api_items(api_url: str = "http://localhost:8001") -> tuple[bool, dict]:
    """Helper to query the REST API endpoint."""
    try:
        response = requests.get(
            f"{api_url}/items/",
            headers={"accept": "application/json", "token": "sg_super_secret_token"},
            timeout=3,
        )
        if response.status_code == 200:
            return True, response.json()
        return False, {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return False, {"error": f"API unreachable at {api_url}: {e}"}


def sidebar_info(logo1: str, logo2: str) -> dict[str, str]:
    """Renders the Streamlit sidebar controls, API/Postgres status, and About section."""
    st.markdown(get_logo_html(logo1, logo2), unsafe_allow_html=True)
    st.divider()

    st.markdown("### Settings & Options")
    selected_model = st.selectbox(
        "Select Model",
        options=["llama3.1", "gemma", "none"],
        index=0,
        help="Choose the model mode for the application.",
    )

    selected_embedding = st.selectbox(
        "Select Embedding",
        options=["bge-m3", "nomic-embed-text-v1", "none"],
        index=0,
        help="Choose the embedding mode.",
    )

    st.divider()

    st.markdown("### Integrations")

    # Test Postgres Button
    if st.button("Check Postgres DB", use_container_width=True):
        success, msg = check_postgres_connection()
        if success:
            st.success(msg)
        else:
            st.warning(msg)

    # Test REST API Button
    if st.button("Fetch REST API Items", use_container_width=True):
        success, data = fetch_api_items()
        if success:
            st.json(data)
        else:
            st.info(data.get("error", "API unavailable"))

    st.divider()

    st.markdown("### Environment Status")
    st.caption(f"**DB Host:** `{settings.DB_HOST}:{settings.DB_PORT}`")
    st.caption(f"**DB Name:** `{settings.DB_NAME}`")
    st.caption(f"**Log Level:** `{settings.LOG_LEVEL}`")

    st.divider()
    st.markdown("### About")
    st.caption(
        "**SG Project Template**\n\n"
        "Built with Streamlit & Clean Architecture.\n\n"
        "© Deduce Data Solutions"
    )

    return {
        "model": selected_model,
        "embedding": selected_embedding,
    }
