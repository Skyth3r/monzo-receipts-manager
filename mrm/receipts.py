from mrm.monzo import Monzo
from mrm.models import Receipt, Item, SubItem, Tax, Payment, Merchant
from mrm.serializers import ReceiptSchema
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
receipt = Receipt(
    transaction = transaction.get('id'),
    receipt_id = input("Receipt Number: "),
    total = int(input("Total in pennies: ")),
    currency = input("Currency (e.g: GBP): "),
)
while True:
    print(f"Item {len(receipt.items)+1}")
    item = Item(
        description = input("Description: "),
        amount = int(input("Amount in pennies: ")),
        currency = input("Currency (e.g: GBP): "),
        quantity = float(input("Quantity: ")),
        unit = input("Unit: "),
        tax = int(input("Tax in pennies: ")),
    )
    receipt.add_item(item)
    if not strtobool(input("Do you want to add more items? (y/n)\n").lower()):
        break

if strtobool(input("Do you have tax information to add? (y/n)\n").lower()):
    while True:
        print(f"Tax item {len(receipt.taxes)+1}")
        tax = Tax(
            description = input("Description: "),
            amount = int(input("Amount in pennies: ")),
            currency = input("Currency (e.g: GBP): "),
        )
        receipt.add_tax(tax)
        if not strtobool(input("Do you want to add more items? (y/n)\n").lower()):
            break

if strtobool(input("Do you have payment information to add? (y/n)\n").lower()):
    while sum([x.amount for x in receipt.payments]) < receipt.total:
        print(f"Payment method {len(receipt.payments)+1}, {receipt.total-sum([x.amount for x in receipt.payments])} remaining")
        payment = Payment(
            type = input("Payment type (choices: card, cash, gift_card): "),
            amount = int(input("Amount in pennies: ")),
            currency = input("Currency (e.g: GBP): "),
        )
        if payment.type == 'card':
            payment.last_four = input("Last four digits of card: ")
        elif payment.type == 'gift_card':
            payment.gift_card_type = input("Type of gift card or coupon")
        receipt.add_payment(payment)

if strtobool(input("Do you have merchant information to add? (y/n)\n").lower()):
    merchant = Merchant(
        name=input("Name: "),
        online=strtobool(input("Online (y/n): ")),
        phone=input("Phone: "),
        email=input("Email: "),
        store_name=input("Branch: "),
        store_address=input("Address (without postcode): "),
        store_postcode=input("Postcode: ")
    )
    receipt.set_merchant(merchant)

schema = ReceiptSchema()
pp(schema.dump(receipt))

if strtobool(input("Does this look right? (y/n)\n")):
    receipt_r = client.create_reciept(receipt)
    if receipt_r:
        print('All ok!')
    else:
        print('Failure')
        print(receipt_r.data)
else:
    exit()
