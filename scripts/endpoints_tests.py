import inspect

import budgea
from budgea import ApiException
from marshmallow import ValidationError
from marshmallow.fields import Field
from tabulate import tabulate
from budgea.api import *

from scripts.utils import get_client, APPLICATION_CREDENTIALS

apis = dir(budgea.api)

ok = []
nok = []

for api in apis:
    if api.endswith('Api'):
        api_class = getattr(budgea, api)
        clients = {
            'client': get_client(APPLICATION_CREDENTIALS['user']['budgea']['access_token']),
            'manage_users': get_client(APPLICATION_CREDENTIALS['budgea']['manage']['users']),
            'manage_config': get_client(APPLICATION_CREDENTIALS['budgea']['manage']['config']),
            'manage_facturation': get_client(APPLICATION_CREDENTIALS['budgea']['manage']['facturation']),
        }

        methods = [m for m in dir(api_class) if m.endswith('_get')]

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
        for k, client in clients.items():
            instance = api_class(api_client=client)
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
                    nok.append([k, api, method, endpoint])
                except ValidationError as e:
                    print(e)
                    return_type = None
                    for l in inspect.getdoc(bounded_method).splitlines():
                        if ':return:' in l:
                            return_type = l.split(':return:')[1].strip()
                            if hasattr(budgea.models, return_type):
                                break
                    for field_name, messages in e.messages.items():
                        if Field.default_error_messages['null'] in messages and return_type:
                            schema_type = '/components/schemas/%s' % return_type
                            print('{"op": "add", "path": "%s/properties/%s/nullable", "value": true},' % (schema_type, field_name))

                    nok.append([k, api, method, endpoint])
                # print(data)
                ok.append([k, api, method, endpoint])


print('OK:')
print(tabulate(sorted(ok, key=lambda r: r[3])))
print('NOK:')
print(tabulate(sorted(nok, key=lambda r: r[3])))

