from budgea import BanksApi

from scripts.utils import get_client, APPLICATION_CREDENTIALS

client = get_client(APPLICATION_CREDENTIALS['user']['budgea']['access_token'])

id_account = 94

BanksApi(api_client=client).usersid_user_accountsid_account_transactionsclusters_post('me', 94, mean_amount=0, wording="test",
    next_date="2020-15-03", _preload_content=False)
