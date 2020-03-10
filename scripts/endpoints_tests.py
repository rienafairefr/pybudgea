import inspect

import budgea
from budgea import ApiException
from marshmallow import ValidationError
from tabulate import tabulate
from budgea.api import *

from scripts.utils import get_client, APPLICATION_CREDENTIALS

apis = dir(budgea.api)

ok = []
nok = []

for api in apis:
    if api.endswith('Api'):
        api_class = getattr(budgea, api)

        user_client = get_client(APPLICATION_CREDENTIALS['user']['budgea']['access_token'])
        admin_client_users = get_client(APPLICATION_CREDENTIALS['budgea']['manage']['users'])
        admin_client_config = get_client(APPLICATION_CREDENTIALS['budgea']['manage']['config'])
        admin_client_facturation = get_client(APPLICATION_CREDENTIALS['budgea']['manage']['facturation'])

        instance = api_class(api_client=user_client)
        methods = [m for m in dir(instance) if m.endswith('_get')]

        # kwargs = dict(_preload_content=False)
        id_client = 95221982
        id_webhooks = 1
        id_user = 'me'
        id_webhook = 56
        id_account = 94
        id_account_type = 1
        id_connector = 510
        id_connection = 1
        id_investment = 1
        id_transaction = 10057
        id_information = 1
        id_transactions_cluster = 1
        id_subscription = 1
        id_device = 1
        id_profile = 1
        id_security = 1
        id_recipient = 1
        type = 'test'
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
            kwargs = dict()
            string_value = '%s(api_client=client).%s%s' % (api, method, signature)
            print(string_value)
            try:
                data = eval(string_value)
            except ApiException as e:
                print(e)
                nok.append([api, method, endpoint])
            except ValidationError as e:
                print(e)
                nok.append([api, method, endpoint])
            print(data)
            if data.status == 200:
                ok.append([api, method, endpoint])
            else:
                nok.append([api, method, endpoint])


print('OK:')
tabulate(ok)
print('NOK:')
tabulate(nok)



#print(tabulate(results))
