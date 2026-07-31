"""Streamlit UI Application for sg_project_template."""

import sys
from pathlib import Path
import streamlit as st
from loguru import logger

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.infra.logging import setup_logger
from src.presentation.ui.assets import (
    get_base64_image,
    hide_anchor_css,
    hide_buttons_css,
)
from src.presentation.ui.sidebar import sidebar_info


def initialize_session_state() -> None:
    """Initialize Streamlit session state keys."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! How can I assist you with SG Project Template today?",
            }
        ]


def main_ui() -> None:
    """Main Streamlit application layout and execution flow."""
    setup_logger(level="DEBUG")
    initialize_session_state()

    logo_url = "https://deduceds.github.io/assets/images/logo/logo_horizontal_mini.png"
    st.set_page_config(
        page_title="SG Project Template",
        page_icon="data/assets/images/favicon.ico",
        layout="wide",
        menu_items={
            "About": f"### Built by ![**Deduce Data Solutions**]({logo_url})\n\n**SG Project Template** - Streamlit Clean Architecture."
        },
    )

    st.markdown(hide_buttons_css, unsafe_allow_html=True)
    st.markdown(hide_anchor_css, unsafe_allow_html=True)

    # Encode logo images if present
    logo1 = get_base64_image("data/assets/images/logo2.png")
    logo2 = get_base64_image("data/assets/images/logo.png")

    # Render Sidebar
    with st.sidebar:
        ui_config = sidebar_info(logo1, logo2)

    # Render Main Panel Header
    st.title("SG Project Template Chatbot")
    st.caption(f"Running with **Model:** `{ui_config['model']}` | **Embedding:** `{ui_config['embedding']}`")

    # Display Chat Messages
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat Input Box
    if user_prompt := st.chat_input("Enter your message..."):
        # Log and display user message
        logger.info(f"User message: {user_prompt}")
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_prompt)

        # Generate Assistant Response
        assistant_response = f"Echo response for: **{user_prompt}** (Model: `{ui_config['model']}`)"
        logger.info(f"Assistant response: {assistant_response}")
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(assistant_response)


if __name__ == "__main__":
    main_ui()
