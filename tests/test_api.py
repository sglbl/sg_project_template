'''
This file tests the API endpoint by sending requests and checking responses.
'''

import os
import pytest
import requests
from loguru import logger
from src.infra.logging import setup_logger

setup_logger("TRACE")


def get_api_url(local_or_remote: str) -> str:
    if local_or_remote == "remote":
        return os.environ.get("API_URL", "https://sgproject.url")
    else:
        return os.environ.get("API_URL", "http://localhost:8001")


@pytest.mark.integration
def test_item_retrieval(args):
    api_url = get_api_url(local_or_remote=args.access)
    endpoint = "items/"

    headers = {
        'accept': 'application/json',
        'token': 'sg_super_secret_token',
    }

    response = requests.get(
        f"{api_url}/{endpoint}",
        headers=headers
    )

    logger.opt(colors=True).debug(f"\nRetrieving items: (Status code: {response.status_code})")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    result = response.json()
    assert result, "Response JSON is empty"
    logger.opt(colors=True).trace(f"<i><u>Items retrieved:</u></i> {result}")