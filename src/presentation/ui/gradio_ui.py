import base64
import os
import time
import gradio as gr
import pprint
from src.infra.database.db_engine import insert_validated_data
from src.application.api_services import *
from src.presentation.ui.asset import *

# examples=[["Where did normans invade"], ["where did normans invade, answer in english"]]
examples = [[{"text": "Where did normans invade", "files": []}], [{"text": "where did normans invade, answer in english", "files": []}]]


def add_to_db(x: gr.LikeData):
    # print(x.index, x.value, x.liked)
    print(f"Adding 'liked: {x.liked}' data to database...")
    all_dict_labels_with_entities = {}
    
    # Convert sets to lists to make the dictionary JSON serializable
    all_dict_labels_with_entities = {}
    for key, value in labels_with_entities.items():
        if isinstance(value, set):
            all_dict_labels_with_entities[key] = list(value)
        else:
            all_dict_labels_with_entities[key] = value
    
    insert_validated_data(
        prompt=last_question,
        entities=all_dict_labels_with_entities,
        json_data={"answer": model_result[-1]},
        feedback=x.liked
    )    


def ask_and_get_trigger(history, chat_text_input):
    global model_result, unique_label_len, last_question, labels_with_entities
    last_question = chat_text_input
    # model_result, unique_label_len, labels_with_entities = ask_to_nlp_model(chat_text_input)
    # response = json_to_md_table(model_result[0:unique_label_len])
    print(f"User input: {chat_text_input}")
    model_result = f"Answering the question: {chat_text_input}"
    response = model_result

    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        if character == "}":
         time.sleep(0.0001)
        yield history

def add_user_message(history, message):
    return history + [[message["text"], None]]


def add_user_dont_like_message(history):
    other_response = "Showing other possible results...\n" + pprint.pformat(model_result[unique_label_len:], indent=2)
    ret_res = history + [["I didn't like the results, show me others",  other_response]]

    return ret_res


def add_info_to_database_liked(): 
    # Example usage
    insert_validated_data(
        prompt=last_question,
        json_data={"answer": model_result[-1]},
        feedback=True,
    )    


def add_info_to_database_disliked():
    # Example usage
    insert_validated_data(
        prompt=last_question,
        json_data={"answer": model_result[-1]},
        feedback=False,
    )


def run_ui():
    # Run the app
    with gr.Blocks(css=gradio_css, title="Sg GPT") as demo:        
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
            likeable=True
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

        # button_hidden_other_results.click(add_user_dont_like_message, inputs=[chatbot], outputs=[chatbot])

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

        bot_msg = user_msg1.then(ask_and_get_trigger, inputs=[chatbot, chat_text_input], outputs=chatbot)
        # bot_msg = user_msg2.then(ask_and_get_trigger, inputs=[chatbot, chat_text_input], outputs=chatbot)

        with gr.Row():
            gr.Examples(examples=examples, inputs=[chat_text_input], cache_examples=False)

    demo.queue()

    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=os.getenv("GRADIO_SERVER_PORT", 8000),
        favicon_path="./data/images/favicon.ico"
    )

if __name__ == "__main__":
    print("Please run src.main with -m mod parameter [python -m src.main]")
