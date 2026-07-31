import base64
import streamlit as st


def get_base64_image(image_path: str) -> str:
    """Encodes an image file to base64 string for Markdown/HTML embedding."""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""


hide_buttons_css = """
    <style>
        .stAppDeployButton {display:none;}
        
        /* Targets the specific Streamlit footer in About section */
        div[data-testid="stMarkdownContainer"] p:has(a[href="https://streamlit.io"]) {
            display: none;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            width: min(400px, 30vw) !important;
        }
    </style>
"""

hide_anchor_css = """
    <style>
        /* Hide standard header anchor links */
        h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
            display: none !important;
        }
        [data-testid="stHeaderActionElements"] {
            display: none !important;
        }
        div[data-testid="StyledLinkIconContainer"] {
            display: none !important;
        }
    </style>
"""


def get_logo_html(logo1_base64: str, logo2_base64: str) -> str:
    """Renders formatted HTML header logos for sidebar."""
    html = "<div style='text-align: center; margin-bottom: 15px;'>"
    if logo1_base64:
        html += f'<img src="data:image/png;base64,{logo1_base64}" style="width: 80%; max-width: 160px; height: auto;" /><br>'
    html += (
        "<span style='display: inline-block; margin: 4px 0; font-size: 13px; color: #888; font-style: italic;'>by</span><br>"
    )
    if logo2_base64:
        html += (
            f'<a href="https://deducedata.solutions" target="_blank" rel="noopener noreferrer">'
            f'<img src="data:image/png;base64,{logo2_base64}" style="width: 70%; max-width: 130px; height: auto;" alt="Deduce Logo" />'
            f'</a>'
        )
    else:
        html += "<strong style='color: #4A90E2;'>SG Project Template</strong>"
    html += "</div>"
    return html
