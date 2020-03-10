import json
import os

from budgea import Configuration, ApiClient
from dotenv import load_dotenv


load_dotenv()

APPLICATION_CREDENTIALS = json.load(open(os.environ['APPLICATION_CREDENTIALS']))

BUDGEA_HOST = APPLICATION_CREDENTIALS['budgea']['host']
BUDGEA_CLIENT_ID = APPLICATION_CREDENTIALS['budgea']['client_id']
BUDGEA_CLIENT_SECRET = APPLICATION_CREDENTIALS['budgea']['client_secret']
BUDGEA_MANAGE_TOKEN_CONFIG = APPLICATION_CREDENTIALS['budgea']['manage']['config']


def get_client(token):
    config = Configuration()

    config.host = BUDGEA_HOST
    config.api_key['client_id'] = BUDGEA_CLIENT_ID
    config.api_key['client_secret'] = BUDGEA_CLIENT_SECRET
    config.api_key['Authorization'] = token
    config.api_key_prefix['Authorization'] = 'Bearer'
    return ApiClient(config)

