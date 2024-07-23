import gradio as gr
from src.ui import *

def get_html_table():
    return """
    <table>
        <thead>
            <tr><th>name   </th><th>identificator    </th><th>physicalPath     </th></tr>
        </thead>
        <tbody>
            <tr><td>QUAKE_1 </td><td>ANTIOCH_QUAKE_1 </td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_10</td><td>ANTIOCH_QUAKE_10</td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_11</td><td>ANTIOCH_QUAKE_11</td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_12</td><td>ANTIOCH_QUAKE_12</td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_13</td><td>ANTIOCH_QUAKE_13</td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_14</td><td>ANTIOCH_QUAKE_14</td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_15</td><td>ANTIOCH_QUAKE_15</td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_16</td><td>ANTIOCH_QUAKE_16</td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_17</td><td>ANTIOCH_QUAKE_17</td><td>HATAY||ANTAKYA</td></tr>
            <tr><td>QUAKE_18</td><td>ANTIOCH_QUAKE_18</td><td>HATAY||ANTAKYA</td></tr>
        </tbody>
    </table>
    """
    
examples=[["Find me all earthquakes", 10]]

def add_user_message(history, message):
    return history + [[message, None]]


def ask_and_get_trigger(history):
    response = get_html_table()
    
    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        yield history, None
        
    values_to_show = [5, 10] 
    yield history, gr.Dropdown(choices=values_to_show, value=10, allow_custom_value=True)


if __name__ == "__main__":
    with gr.Blocks(js=js_refresh, css="footer {visibility: hidden}", title="SG Project") as demo:
        # Header with logo
        gr.Markdown(logo_with_title)
        
        chatbot = gr.Chatbot([],
                elem_id="chatbot",
                bubble_full_width=False)
        with gr.Row():
            chat_text_input = gr.Textbox(label="Question", placeholder="Type your question here")
            values_to_show = [i for i in range(10, 101, 10)] # show results from 10 to 100 in steps of 10
            chat_dropdown_input = gr.Dropdown(values_to_show, label="Number of results to show", value=10, allow_custom_value=True, interactive=True)

        user_msg1 = chat_text_input.submit(add_user_message, [chatbot, chat_text_input], [chatbot])
        bot_msg = user_msg1.then(ask_and_get_trigger, inputs=[chatbot], outputs=[chatbot, chat_dropdown_input])

        # Examples table row
        with gr.Row():
            gr.Examples(examples=examples, inputs=[chat_text_input, chat_dropdown_input])
                
        # Change color theme row instead of the footer
        with gr.Row():
            with gr.Column(scale=3): pass
            button_change_color_theme = gr.Button("Change Color Theme⚙️", size="sm")
            with gr.Column(scale=3): pass
            button_change_color_theme.click(None, js=js_change_color_theme)


    # gr.HTML("""<img src="/file=data/images/logo.png"/>""")

    demo.launch(debug=True, allowed_paths=["data/images"], show_error=True)