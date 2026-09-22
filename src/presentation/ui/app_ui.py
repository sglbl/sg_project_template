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
        page_icon="src/presentation/ui/assets/favicon.ico",
        layout="wide",
        menu_items={
            "About": f"### Built by ![**Deduce Data Solutions**]({logo_url})\n\n**SG Project Template** - Streamlit Clean Architecture."
        },
    )

    st.markdown(hide_buttons_css, unsafe_allow_html=True)
    st.markdown(hide_anchor_css, unsafe_allow_html=True)

    # Encode logo images if present
    logo1 = get_base64_image("src/presentation/ui/assets/logo2.png")
    logo2 = get_base64_image("src/presentation/ui/assets/logo.png")

    # Render Sidebar
    with st.sidebar:
        ui_config = sidebar_info(logo1, logo2)

    # Main Layout Tabs
    tab_chat, tab_ml_infer, tab_ml_drift = st.tabs([
        "💬 Assistant Chat",
        "⚡ Model Serving & Inference Sandbox",
        "📊 Data Drift & MLOps Monitoring",
    ])

    with tab_chat:
        st.subheader("SG Project Template Chatbot")
        st.caption(f"Running with **Model:** `{ui_config['model']}` | **Embedding:** `{ui_config['embedding']}`")

        # Display Chat Messages
        for msg in st.session_state.messages:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # Chat Input Box
        if user_prompt := st.chat_input("Enter your message..."):
            logger.info(f"User message: {user_prompt}")
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_prompt)

            assistant_response = f"Echo response for: **{user_prompt}** (Model: `{ui_config['model']}`)"
            logger.info(f"Assistant response: {assistant_response}")
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(assistant_response)

    with tab_ml_infer:
        st.subheader("⚡ Low-Latency ONNX Model Serving Sandbox")
        from src.application.services.inference_service import InferenceService
        from src.domain.schemas.ml_schemas import PredictRequest

        try:
            service = InferenceService()
            engine_badge = "ONNX Runtime 🚀" if service._onnx_engine else "Scikit-Learn (Fallback) 📦"
            model_name = Path(service.active_model_path).name if service.active_model_path else "None loaded"

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Active Model", model_name)
            col_m2.metric("Inference Engine", engine_badge)
            col_m3.metric("Status", "Operational 🟢" if service.active_model_path else "No Model Found 🔴")

            st.markdown("---")
            st.write("##### Input Features")

            col1, col2 = st.columns(2)
            with col1:
                sepal_len = st.slider("Sepal Length (cm)", min_value=4.0, max_value=8.0, value=5.1, step=0.1)
                sepal_wid = st.slider("Sepal Width (cm)", min_value=2.0, max_value=5.0, value=3.5, step=0.1)
            with col2:
                petal_len = st.slider("Petal Length (cm)", min_value=1.0, max_value=7.0, value=1.4, step=0.1)
                petal_wid = st.slider("Petal Width (cm)", min_value=0.1, max_value=3.0, value=0.2, step=0.1)

            if st.button("🔮 Run Prediction", type="primary"):
                req = PredictRequest(
                    features={
                        "sepal_length": sepal_len,
                        "sepal_width": sepal_wid,
                        "petal_length": petal_len,
                        "petal_width": petal_wid,
                    }
                )
                res = service.predict(req)
                target_names = {0: "Setosa", 1: "Versicolour", 2: "Virginica"}
                label_name = target_names.get(int(res.prediction), f"Class {res.prediction}")

                st.success(f"**Predicted Class:** `{label_name}` (Raw: `{res.prediction}`)")
                st.info(f"⏱️ **Inference Latency:** `{res.execution_time_ms} ms` | **Engine:** `{engine_badge}`")
        except Exception as e:
            st.error(f"Inference service error: {e}. Train a model first via `python -m src.main train`.")

    with tab_ml_drift:
        st.subheader("📊 Evidently Data & Target Drift Monitoring")
        from src.application.pipelines.evaluate import ModelEvaluationPipeline

        ref_file = Path("data/processed/dataset_train.parquet")
        cur_file = Path("data/processed/dataset_test.parquet")

        col_d1, col_d2 = st.columns(2)
        col_d1.info(f"**Reference Baseline:** `{ref_file}` ({'Found' if ref_file.exists() else 'Missing'})")
        col_d2.info(f"**Current Production Data:** `{cur_file}` ({'Found' if cur_file.exists() else 'Missing'})")

        if st.button("📈 Run Drift Analysis"):
            if not ref_file.exists() or not cur_file.exists():
                st.warning("Please run `python -m src.main ingest` to create baseline and test datasets first.")
            else:
                with st.spinner("Analyzing feature distributions and drift metrics..."):
                    eval_pipe = ModelEvaluationPipeline()
                    drift_detected, drift_share, html_path = eval_pipe.run_drift_analysis(
                        str(ref_file), str(cur_file), report_name="ui_drift_report"
                    )

                    if drift_detected:
                        st.error(f"🚨 **Dataset Drift Detected!** Drifted feature share: `{drift_share:.1%}`")
                    else:
                        st.success(f"✅ **No Significant Drift Detected.** Drifted feature share: `{drift_share:.1%}`")

                    # Display HTML Report
                    if Path(html_path).exists():
                        with open(html_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        st.components.v1.html(html_content, height=800, scrolling=True)


if __name__ == "__main__":
    main_ui()
