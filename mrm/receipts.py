import datetime
import requests
import json
import os
from pprint import pprint as pp
from prettytable import PrettyTable
from distutils.util import strtobool
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
    return (r.status_code == 200, None if r.status_code == 200 else r.json())


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
        'ID',
        'Description',
        'Amount',
        'Currency',
        'Notes',
        'Datetime'
    ]
)
for transaction in transactions:
    transactions_table.add_row(
        [
            transaction.get('id'),
            transaction.get('description'),
            transaction.get('amount')/100,
            transaction.get('currency'),
            transaction.get('notes'),
            humanize.naturalday(parse(transaction.get('created'))),
        ]
    )
print(transactions_table)


transaction = get_transaction(input("ID of transaction you want to add a receipts to: "))
receipt = {}
receipt['transaction_id'] = transaction.get('id')
receipt['external_id'] = input("Receipt Number: ")
receipt['total'] = int(input("Total in pennies: "))
receipt['currency'] = input("Currency (e.g: GBP): ")
receipt['items'] = []
done_adding_items = False
while not done_adding_items:
    if len(receipt['items']) == 0:
        print('This is required! ')
    print(f"Item {len(receipt['items'])+1}")
    item = {}
    item['description'] = input("Description: ")
    item['amount'] = int(input("Amount in pennies: "))
    item['currency'] = input("Currency (e.g: GBP): ")
    item['quantity'] = float(input("Quantity: "))
    item['unit'] = input("Unit: ")
    receipt['items'].append(item)
    if not strtobool(input("Do you want to add more items? (y/n)\n").lower()):
        done_adding_items = True

if strtobool(input("Do you have tax information to add? (y/n)\n").lower()):
    print("Taxes not currently supported.")

if strtobool(input("Do you have payment information to add? (y/n)\n").lower()):
    print("Payments not currently supported.")

if strtobool(input("Do you have merchant information to add? (y/n)\n").lower()):
    print("Merchant info not currently supported.")

pp(receipt)

if strtobool(input("Does this look right? (y/n)\n")):
    receipt = create_reciept(receipt)
    if receipt[0]:
        print('All ok!')
    else:
        print('Failure')
        print(receipt[1])
else:
    exit()
