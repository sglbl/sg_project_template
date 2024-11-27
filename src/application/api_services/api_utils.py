import os
import json
import requests
import dotenv
from loguru import logger

true = True; false = False

def get_token(domain):
    # Get the scret for token from the environment variables file and return it
    dotenv.load_dotenv(override=True)
    secret_key = os.getenv('CLIENT_SECRET')
    
    if secret_key is None:
        raise ValueError("You need to put the secret key (that is needed to generate token) in .env file")
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': 'deduce',
        'client_secret': secret_key,
    }

    try:
        response = requests.post(f'https://{domain}/token', data=data, timeout=10)
        return response.json()['access_token']
    except KeyError as e:
        print(f"Error in getting token: {response.text}")
        raise ValueError(f"Error in {e}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error in connection. Make sure VPN is connected. Details: {e}")

    