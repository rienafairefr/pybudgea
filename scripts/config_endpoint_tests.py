import json

from budgea import AdministrationApi

from scripts.utils import get_client, APPLICATION_CREDENTIALS

BUDGEA_MANAGE_TOKEN_CONFIG = APPLICATION_CREDENTIALS['budgea']['manage']['config']

client = get_client(BUDGEA_MANAGE_TOKEN_CONFIG)
api = AdministrationApi(api_client=client)

data = api.config_get(_preload_content=False)

print(json.loads(data.data))