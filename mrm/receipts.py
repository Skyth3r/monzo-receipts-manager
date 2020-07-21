from mrm.monzo import Monzo
from pprint import pprint as pp
from prettytable import PrettyTable
from distutils.util import strtobool
from dateutil.parser import parse
import humanize


client = Monzo()

# List Account and ask user to pick one!
accounts = client.list_accounts()
if not accounts:
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
for option, acct in (enumerate(accounts.data)):
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
account = accounts.data[int(input("Please choose an account from above: "))]

# Load Tranactions

print(f"Loading transactions from the past week for account_id `{account.get('id')}`")
transactions = client.list_transactions(account.get('id'))
if len(transactions.data) == 0:
    print("No transactions found! Exiting!")
    exit()
else:
    print(f"{len(transactions.data)} transactions found")
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
for transaction in transactions.data:
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


transaction = client.get_transaction(input("ID of transaction you want to add a receipts to: ")).data
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
    receipt = client.create_reciept(receipt)
    if receipt:
        print('All ok!')
    else:
        print('Failure')
        print(receipt.data)
else:
    exit()
