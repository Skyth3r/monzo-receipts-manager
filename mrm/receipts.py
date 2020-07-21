import datetime
import requests
import json
import os
from pprint import pprint as pp
from prettytable import PrettyTable
from dateutil.parser import parse
import humanize

MONZO_API_BASE = 'https://api.monzo.com'

MONZO_CLIENT_ID = os.environ['MONZO_CLIENT_ID']
MONZO_CLIENT_SECRET = os.environ['MONZO_CLIENT_SECRET']

MONZO_TOKEN = json.loads(os.environ['MONZO_TOKEN'])


def get_headers(**kwargs):
    kwargs['Authorization'] = "Bearer " + MONZO_TOKEN['access_token']
    return kwargs


def list_accounts():
    url = MONZO_API_BASE+'/accounts/'
    method = 'GET'
    headers = get_headers()
    r = requests.request(method, url, headers=headers)
    return r.json().get('accounts')


def list_transactions(
    account_id: str,
    since: datetime.datetime = None,
    before: datetime.datetime = None,
):
    url = MONZO_API_BASE + '/transactions/'
    method = 'GET'
    if not since:
        since = (
            datetime.datetime.utcnow().astimezone()-datetime.timedelta(days=7)
            )
    if not before:
        before = datetime.datetime.utcnow().astimezone()
    headers = get_headers()
    params = {
        'account_id': account_id,
        'since': since.isoformat(),
        'before': before.isoformat()
    }
    print(f"Loading transactions between {since} and {before}")
    r = requests.request(method, url, headers=headers, params=params)
    return r.json().get('transactions')


def get_transaction(transaction_id: str):
    url = MONZO_API_BASE+'/transactions/'+transaction_id
    method = 'GET'
    headers = get_headers(**{'expand[]': 'merchant'})
    r = requests.request(method, url, headers=headers)
    return r.json().get('transaction')


def create_reciept(params: dict):
    url = MONZO_API_BASE+'/transaction-receipts/'
    method = 'PUT'
    headers = get_headers()
    r = requests.request(method, url, headers=headers, json=params)
    return r.status_code == 200


# List Account and ask user to pick one!
accounts = list_accounts()
if accounts is None:
    print('Please authorize us in your app!')
    exit()
accounts_table = PrettyTable(
    [
        '',
        'Type',
        'Sort Code',
        'Account Number',
        'Description',
        'Active',
    ]
)
for option, acct in (enumerate(accounts)):
    accounts_table.add_row(
        [
            option,
            acct.get('type'),
            acct.get('sort_code'),
            acct.get('account_number'),
            acct.get('description') if (acct.get('type') == 'uk_business') else ' & '.join([x.get('preferred_name') for x in acct.get('owners')]),
            not acct.get('closed'),
        ]
    )
print(accounts_table)
account = accounts[int(input("Please choose an account from above: "))]

# Load Tranactions

print(f"Loading transactions from the past week for account_id `{account.get('id')}`")
transactions = list_transactions(account.get('id'))
if len(transactions) == 0:
    print("No transactions found! Exiting!")
    exit()
else:
    print(f"{len(transactions)} transactions found")
transactions_table = PrettyTable(
    [
        '',
        'Description',
        'Amount',
        'Currency',
        'Notes',
        'Datetime'
    ]
)
for option, transaction in enumerate(transactions):
    transactions_table.add_row(
        [
            option,
            transaction.get('description'),
            transaction.get('amount')/100,
            transaction.get('currency'),
            transaction.get('notes'),
            humanize.naturalday(parse(transaction.get('created'))),
        ]
    )
print(transactions_table)
