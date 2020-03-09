import json

import budgea
from budgea import Configuration, ApiClient
from budgea.api import *

apis = dir(budgea.api)

APPLICATION_CREDENTIALS = json.load(open('../.secrets/secrets.json'))

BUDGEA_HOST = APPLICATION_CREDENTIALS['budgea']['host']
BUDGEA_CLIENT_ID = APPLICATION_CREDENTIALS['budgea']['client_id']
BUDGEA_CLIENT_SECRET = APPLICATION_CREDENTIALS['budgea']['client_secret']
BUDGEA_MANAGE_TOKEN_CONFIG = APPLICATION_CREDENTIALS['budgea']['manage_token_config']


def get_client(token):
    config = Configuration()

    config.host = BUDGEA_HOST
    config.api_key['client_id'] = BUDGEA_CLIENT_ID
    config.api_key['client_secret'] = BUDGEA_CLIENT_SECRET
    config.api_key['Authorization'] = token
    config.api_key_prefix['Authorization'] = 'Bearer'
    return ApiClient(config)


user_client = get_client(BUDGEA_MANAGE_TOKEN_CONFIG)
api = AdministrationApi(api_client=user_client)

data = api.config_get(_preload_content=False)

print(json.loads(data.data))