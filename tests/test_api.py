'''
This file tests the API / Model by sending a request with a directory path of files and checking the response.

To get the usage details, run the following command:
pytest src/tests/test_api.py --test-help

Example:
pytest -s src/tests/test_api.py --access local --model llama3.1 --input_path ./data/example_inputs/
'''

import os
import gradio_client as grc
from loguru import logger
from src.application import utils

utils.set_logger("TRACE")

def get_api_url(local_or_remote):
    # Retrieve the API URL from an environment variable or configuration
    # If the environment variable is not set, provide a default URL
    if local_or_remote == "remote":
        return os.environ.get("API_URL", "https://sgproject.url")
    else:  # local
        return os.environ.get("API_URL", "http://localhost:8000")


def test_queries(args, question):
    # Construct the API URL dynamically
    api_url = get_api_url(local_or_remote=args.access)
    client = grc.Client(api_url)

    input_file_paths = [grc.handle_file(os.path.join(args.input_path, file)) for file in os.listdir(args.input_path)]
        
    result = client.predict(
        history=[["Answer the question if the file has answer", None]],
        chat_text_input={"text": question, "files": input_file_paths},
        api_name="/ask_and_get_trigger"
    )

    logger.opt(colors=True).debug(f"\n<i><u>Question:</u></i> {question}")
    logger.opt(colors=True).trace(f"<i><u>Answer:</u></i> {result[0][1]}")

