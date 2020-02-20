import inspect
import json

from tabulate import tabulate

import budgea
from budgea import Configuration, ApiClient, ApiException
from budgea.api import *

apis = dir(budgea.api)

APPLICATION_CREDENTIALS = json.load(open('../.secrets/credentials.json'))
ADMIN_APPLICATION_CREDENTIALS = json.load(open('../.secrets/budgea-admin.json'))

BUDGEA_HOST = APPLICATION_CREDENTIALS['budgea']['host']
BUDGEA_CLIENT_ID = APPLICATION_CREDENTIALS['budgea']['client_id']
BUDGEA_CLIENT_SECRET = APPLICATION_CREDENTIALS['budgea']['client_secret']


def get_client(token):
    config = Configuration()

    config.host = BUDGEA_HOST
    config.api_key['client_id'] = BUDGEA_CLIENT_ID
    config.api_key['client_secret'] = BUDGEA_CLIENT_SECRET
    config.api_key['Authorization'] = token
    config.api_key_prefix['Authorization'] = 'Bearer'
    return ApiClient(config)

ok = []
nok = []

for api in apis:
    if api.endswith('Api'):
        api_class = getattr(budgea, api)

        user_client = get_client(APPLICATION_CREDENTIALS['user']['budgea']['access_token'])
        admin_client_users = get_client(ADMIN_APPLICATION_CREDENTIALS['users'])
        admin_client_config = get_client(ADMIN_APPLICATION_CREDENTIALS['users'])
        admin_client_facturation = get_client(ADMIN_APPLICATION_CREDENTIALS['facturation'])

        instance = api_class(api_client=user_client)
        methods = [m for m in dir(instance) if m.endswith('_get')]

        kwargs = dict(_preload_content=False)
        id_client = 79542495
        id_webhooks = 1
        id_user = 'me'
        id_webhook = 56
        id_account_type = 1
        id_connector = 510
        id_connection = 1
        id_investment = 1
        _type = 'test'
        key = 'key'
        client = user_client

        for method in methods:
            bounded_method = getattr(instance, method)
            signature = inspect.signature(bounded_method)
            src = inspect.getsource(getattr(instance, method+'_with_http_info'))
            idx = src.index('self.api_client.call_api(')
            src = src[idx+26:].strip()[1:]
            idx = src.index("'")
            endpoint = src[:idx]
            kwargs = dict(_preload_content=False)
            string_value = '%s(api_client=client).%s%s' % (api, method, signature)
            print(string_value)
            try:
                data=eval(string_value)
                print(data)
                if data.status == 200:
                    ok.append([api, method, endpoint])
                    continue
            except:
                pass
            nok.append([api, method, endpoint])




print('OK:')
tabulate(ok)
print('NOK:')
tabulate(nok)





#print(tabulate(results))
