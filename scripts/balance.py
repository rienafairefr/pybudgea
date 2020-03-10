from budgea import PFMApi, BanksApi

from scripts.utils import APPLICATION_CREDENTIALS, get_client

user = APPLICATION_CREDENTIALS['user']

client = get_client(user['budgea']['access_token'])

api = PFMApi(client)
banks_api = BanksApi(client)
user_accounts = banks_api.usersid_user_accounts_get('me')

for account in user_accounts.accounts:
    id_account = account.id
    id_connection = account.id_connection

    period = '1year'
    balances = [
        api.usersid_user_balances_get('me', period=period),
        api.usersid_user_accountsid_account_balances_get('me', id_account, period=period),
        api.usersid_user_connectionsid_connection_accountsid_account_balances_get('me', id_connection, id_account,
                                                                                  period=period),
        api.usersid_user_connectionsid_connection_balances_get('me', id_connection, period=period)
    ]

    for ba in balances:
        print(ba)
        for b in ba.balances:
            if len(b.transactions) != 0:
                print(b.transactions)
