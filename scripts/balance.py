import json
import os

from dotenv import load_dotenv

from budgea import Configuration, ApiClient, PFMApi, BanksApi

load_dotenv()

APPLICATION_CREDENTIALS = json.load(open(os.environ['APPLICATION_CREDENTIALS']))

BUDGEA_HOST = APPLICATION_CREDENTIALS['budgea']['host']
BUDGEA_CLIENT_ID = APPLICATION_CREDENTIALS['budgea']['client_id']
BUDGEA_CLIENT_SECRET = APPLICATION_CREDENTIALS['budgea']['client_secret']
user = APPLICATION_CREDENTIALS['user']

config = Configuration()

config.host = BUDGEA_HOST
config.api_key['client_id'] = BUDGEA_CLIENT_ID
config.api_key['client_secret'] = BUDGEA_CLIENT_SECRET
if user and user['budgea']:
    config.api_key['Authorization'] = user['budgea']['access_token']
    config.api_key_prefix['Authorization'] = user['budgea']['access_token_type']
client = ApiClient(config)

api = PFMApi(client)
banks_api = BanksApi(client)
user_accounts = banks_api.users_id_user_accounts_get('me')

for num in range(10):
    id_account = user_accounts.accounts[num].id
    id_connection = user_accounts.accounts[num].id_connection

    period = '1year'
    balances = [
        api.users_id_user_balances_get('me', period=period),
        api.users_id_user_accounts_id_account_balances_get('me', id_account, period=period),
        api.users_id_user_connections_id_connection_accounts_id_account_balances_get('me', id_connection, id_account,
                                                                                     period=period),
        api.users_id_user_connections_id_connection_balances_get('me', id_connection, period=period)
    ]

    for ba in balances:
        print(ba)
        for b in ba.balances:
            if len(b.transactions) != 0:
                print(b.transactions)
