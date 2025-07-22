import base64
import os
import time
import gradio as gr
from src.application.llm_service import *
from src.presentation.ui.asset import *


examples = [[{"text": "Where did normans invade", "files": []}], [{"text": "where did normans invade, answer in english", "files": []}]]


def add_to_db(x: gr.LikeData):
    print(f"Adding 'liked: {x.liked}' data to database...")
    

def ask_and_get_trigger(history, chat_text_input):
    global model_result

    print(f"User input: {chat_text_input}")
    model_result = f"Answering the question: {chat_text_input}"
    model_result, _prompt = llm_service.llm_rag_handler(chat_text_input["text"], chat_text_input["files"])

    history.append({"role": "assistant", "content": ""})
    for character in model_result:
        history[-1]['content'] += character
        if character == "}":
                time.sleep(0.0001)
        yield history


def add_user_message(history, message):
    return history + [{"role": "user", "content": message["text"]}]


def run_ui(llmservice_dependency: LLMService):
    global llm_service
    llm_service = llmservice_dependency
    # Run the app
    with gr.Blocks(title="Sg GPT") as demo:        
        # create title with the logo
        with open("data/images/logo.png", "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
        title_with_logo = f""" <h1 style="text-align:center; font-family:'system-ui'; display:block;">SG GPT</h1>
                            <img src="data:image/jpeg;base64,{logo_base64}" width="100" style='display:block; margin-left: auto; 
                            margin-right: auto; padding-top: 1ch; align-items: center; justify-content: center;'>"""
        # Header with logo
        gr.Markdown(title_with_logo)

        # Question Part
        chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            bubble_full_width=True,
            type="messages"
        )
        with gr.Row():
            with gr.Column(scale=7):
                # chat_text_input = gr.Textbox(label="Question", scale=7, placeholder="Type your question here")
                chat_text_input = gr.MultimodalTextbox(interactive=True, placeholder="Enter message or upload file...", show_label=False, file_types=["text", "other"])
            # with gr.Column(scale=1):
                # chat_text_button = gr.Button(size="lg", elem_id="button", scale=1)
                # button_hidden_other_results = gr.Button(elem_id="hidden_other_results", visible=False)

        with gr.Row():
            see_other_results_button = gr.Button("See Other Possible Results", visible=False)
        with gr.Row():
            global see_other_results_output
            see_other_results_output = gr.Textbox(label="Other Possible Results", value="", visible=False, lines=12)

        #### Use enter key or the button to submit the question
        user_msg1 = chat_text_input.submit(add_user_message, [chatbot, chat_text_input], [chatbot])
        # user_msg2 = chat_text_button.click(add_user_message, inputs=[chatbot, chat_text_input], outputs=[chatbot])


        js_hidden_results = """
            () => {
                if (document.activeElement.getAttribute('aria-label') === 'clicked dislike') {
                    document.getElementById('hidden_other_results').click();
                } else {
                    // Do nothing
                }
            }
        """
        chatbot.like(add_to_db, inputs=None, outputs=None) #, js=js_hidden_results)

        bot_msg = user_msg1.then(ask_and_get_trigger, inputs=[chatbot, chat_text_input], outputs=[chatbot])
        # bot_msg = user_msg2.then(ask_and_get_trigger, inputs=[chatbot, chat_text_input], outputs=chatbot)

        with gr.Row():
            gr.Examples(examples=examples, inputs=[chat_text_input], cache_examples=False)

    demo.queue()

    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", 8000)),
        favicon_path="./data/images/favicon.ico"
    )

if __name__ == "__main__":
    print("Please run src.main with -m mod parameter [python -m src.main]")
