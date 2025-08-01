import os
import requests
import gradio as gr
import gradio_log as grl
from pathlib import Path
from loguru import logger
from src.config import settings
from src.application import utils
from src.presentation.dependencies import *
from src.application.llm_service import *
from src.presentation.ui.asset import custom_js
from src.infra.repo_implementations.qdrant_repository import QdrantDBRepository
from src.infra.repo_implementations.pgvector_repository import PostgresVectorDBRepository


examples = [[{"text": "Give me the all products", "files": []}], 
            [{"text": "Which day has the most consumption?", "files": []}],
            [{"text": "Give me 5 provincias that ends with A", "files": []}],
            [{"text": "What's the customer who made the purchase of the biggest amount of? By purchase i mean the amount of items required in only one order", "files": []}]
        ]


def create_model_for_ui(model_mode):
    if model_mode == "OpenAI" or "gpt" in model_mode:
        llm_pipeline.create_model("gpt-4o-mini", "text-embedding-3-small", Modes.OPENAI)
    # elif "sql" in model_mode.lower():
    else:
        llm_pipeline.create_model(model_mode, "sentence-transformers/msmarco-distilroberta-base-v2", Modes.OLLAMA)
    return gr.update(visible=True)


def ask_question(chat_input, history, model_mode):
    answer = llm_pipeline.ask_rag_pipeline(chat_input)
    return list(answer)[-1]


def get_models_list():
    get_models_response = requests.get(f"{settings.OLLAMA_API_URL}/api/tags", timeout=10)  # if you're outside, run zerotier vpn before
    if get_models_response.status_code != 200:
        print(f"Error fetching models: {get_models_response.status_code}. No models available.")
        return ["No models available"]
    llm_models = [get_models_response.json()["models"][i]["name"] for i in range(len(get_models_response.json()["models"]))]
    llm_models.insert(1, "gpt-4o-mini")  # add the OpenAI models
    return llm_models


def refresh_logs():
    log_file = "/tmp/app_logs.log"
    Path(log_file).unlink(missing_ok=True)
    logger.add(log_file, format = "<lvl>{message}</lvl>", colorize=True, level="DEBUG")

    print(f"Refreshed the content of the log file: {log_file}")


def add_to_db(x: gr.LikeData):
    print(f'Printing liked: {x.liked}')

   
def run_ui(launch_demo: bool = True) -> gr.Blocks:
    # Create a logger
    utils.set_logger("DEBUG", write_to_file=True)
    # Remove the previous db
    utils.refresh_db()
    # Get available models
    all_models = get_models_list()
    
    # Create the interface
    theme = gr.themes.Soft(radius_size="sm", neutral_hue=gr.themes.Color(c100="#FFFFFF", c200="#9399b2", c300="#7f849c", c400="#6c7086", c50="#cdd6f4", c500="#585b70", c600="#45475a", c700="#313244", c800="#1e1e2e", c900="#181825", c950="#11111b"))
    custom_css = "src/presentation/ui/asset/custom_ui.css"        
    title = "My Project"
    with gr.Blocks(title=title, theme=theme, css_paths=custom_css, js=custom_js.js) as demo:
        # create title with the logo
        with gr.Row(elem_classes="row-header") as title:
            logo_with_title = f"""
                <h1 style="text-align:center; bold; display:block; font-family:'Montserrat';">{title}</h1>
                <img src="/gradio_api/file=data/images/logo.png" width="120" style='display:block; margin-left: auto; 
                margin-right: auto; padding-top: 1ch; align-items: center; justify-content: center;'>
            """
            # Header with logo
            gr.Markdown(logo_with_title, elem_classes="md-header")
        
        # Define the different views
        with gr.Column() as data_area:
            with gr.Sidebar(position="left"):
                gr.Markdown("# Selection")
                gr.Markdown("### Use the options below to select a model and dataset!")
                gr.Markdown("Please select the model and the simulation mode", elem_classes="row-header")

                dropdown = gr.Dropdown(choices=all_models, label="Select the model", interactive=True, allow_custom_value=False)
                # create the default model
                qdrantdb = QdrantDBRepository()
                postgresdb = PostgresVectorDBRepository()
                global llm_pipeline
                llm_pipeline = get_llm_service(postgresdb)
                create_model_for_ui(dropdown.value)

            with gr.Column(visible=True) as outputs_view_chatbot:
                # chatbot_ui.show_chatbot(dropdown)
                    # Question Part
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    bubble_full_width=True,
                    type="messages",
                    placeholder="<strong>Your Data Gpt</strong><br>Ask Me Anything",
                    avatar_images=("data/images/avatars/user.png", "data/images/avatars/robot.png"),
                )
                
                button_hidden_other_results = gr.Button(elem_id="hidden_other_results", visible=False)
                _metadata_info = gr.Textbox("Metadata", visible=False)
                # if "sql" in dropdown.value.lower():
                chat = gr.ChatInterface(fn=ask_question, type="messages", chatbot=chatbot, multimodal=True, save_history=True, additional_inputs=[dropdown], additional_outputs=[_metadata_info])
                # else:    
                #     chat = gr.ChatInterface(fn=ask_rag_pipeline, type="messages", chatbot=chatbot, multimodal=True, save_history=True, additional_outputs=[_metadata_info])

                chat.textbox.placeholder = "Enter message or upload file (.csv, .db, .txt)..."
                chat.textbox.file_types = [".csv", ".db", ".txt", ".pdf"]
                chat.textbox.file_count = "multiple"
                chat.textbox.show_label = False
                
                chatbot.like(add_to_db, inputs=None, outputs=None, js=custom_js.metadata_js)

                with gr.Row():
                    gr.Examples(examples=examples, inputs=[chat.textbox], cache_examples=False)


            with gr.Accordion(label="Show Logs", open=False, elem_id="parameters-accordion"):
                grl.Log("/tmp/app_logs.log", dark=True, label="Logs of the application", height=460)

        dropdown.change(create_model_for_ui, inputs=[dropdown], outputs=[outputs_view_chatbot])       

        # When the tab is closed, refresh the logs
        demo.unload(refresh_logs)

    demo.queue()

    if launch_demo:
        demo.launch(
            server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
            server_port=int(os.getenv("GRADIO_SERVER_PORT", 8000)),
            favicon_path="./data/images/favicon.ico",
            allowed_paths=["./data/images", "./data/example_inputs", "/tmp/**"],
            show_error=True,
            show_api=True
        )
    
    # Return the block
    return demo


if __name__ == "__main__":
    """Please run 
    python -m src.presentation.ui.main_ui
    """
    run_ui()
