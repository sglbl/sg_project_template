'''
This file tests the API / Model by sending a request with a directory path of files and checking the response.

To get the usage details, run the following command:
pytest tests/test_api.py --get-help

Example:
pytest -s --tb=line
pytest -s tests/test_api.py --access local --model llama3.1 --input_path ./data/example_inputs/
'''

import os
import requests
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
        return os.environ.get("API_URL", "http://localhost:8001")

def get_gradio_api_url(local_or_remote):
    # Retrieve the Gradio API URL from an environment variable or configuration
    # If the environment variable is not set, provide a default URL
    if local_or_remote == "remote":
        return os.environ.get("GRADIO_API_URL", "https://sgproject.url/gradio")
    else:  # local
        return os.environ.get("GRADIO_API_URL", "http://localhost:8000")


def test_gradio(args, question):
    # Construct the API URL dynamically
    gradio_api_url = get_gradio_api_url(local_or_remote=args.access)
    client = grc.Client(gradio_api_url)
    input_file_paths = [grc.handle_file(os.path.join(args.input_path, file)) for file in os.listdir(args.input_path) if file.endswith(('.csv', '.db', '.txt'))]
    
    result = client.predict(
        message={"text":"Answer the question if the file has answer", "files": input_file_paths},
		param_2="No models available",
		api_name="/chat"
    )

    logger.opt(colors=True).debug(f"\n<i><u>Question:</u></i> {question}")
    assert result, "Response is empty"

    logger.opt(colors=True).trace(f"<i><u>Answer:</u></i> {result}")


def test_item_retrieval(args):
    # Construct the API URL dynamically
    api_url = get_api_url(local_or_remote=args.access)
    endpoint = "items/"

    headers = {
        'accept': 'application/json',
        'token': 'sg_super_secret_token',
    }
    
    # Send a GET request to the API endpoint
    response = requests.get(
        f"{api_url}/{endpoint}",
        headers=headers
    )

    logger.opt(colors=True).debug(f"\nRetrieving items: (Status code: {response.status_code})")
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert result, "Response JSON is empty"

    logger.opt(colors=True).trace(f"<i><u>Items retrieved:</u></i> {result}")