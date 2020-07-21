class SubItem:
    def __init__(self, description: str, amount: int, currency: str = 'GBP', quantity: int = None, unit: str = '', tax: int = None):
        self.description = description
        self.amount = amount
        self.currency = currency
        self.quantity = quantity
        self.unit = unit
        self.tax = tax


class Item:
    def __init__(self, description: str, amount: int, currency: str = 'GBP', quantity: int = 1, unit: str = '', tax: int = None):
        self.description = description
        self.amount = amount
        self.currency = currency
        self.quantity = quantity
        self.unit = unit
        self.tax = tax
        self.sub_items = []
    
    def add_item(self, item: SubItem):
        assert isinstance(item, SubItem)
        self.sub_items.append(item)


class Tax:
    def __init__(self, description: str, amount: int, currency: str = 'GBP', tax_number: str = None):
        self.description = description
        self.amount = amount
        self.currency = currency
        self.tax_number = tax_number


class Payment:
    def __init__(self, type: str, amount: int, currency: str = 'GBP', last_four: str = None, gift_card_type: str = None, **kwargs):
        self.type = type
        assert self.type in ('card', 'cash', 'gift_card')
        self.amount = amount
        self.currency = currency
        self.last_four = last_four
        self.gift_card_type = gift_card_type
        self.other_metadata = kwargs


class Merchant:
    def __init__(self, name: str, online: bool, phone: str, email: str, store_name: str, store_address: str, store_postcode: str):
        self.name = name
        self.online = online
        self.phone = phone
        self.email = email
        self.store_name = store_name
        self.store_address = store_address
        self.store_postcode = store_postcode


class Receipt:
    def __init__(self, transaction: str, receipt_id: str, total: int, currency: str = 'GBP'):
        self.transaction = transaction
        self.receipt_id = receipt_id
        self.total = total
        self.currency = currency
        self.items = []
        self.taxes = []
        self.payments = []
        self.merchant = None
        
    def add_item(self, item: Item):
        assert isinstance(item, Item)
        self.items.append(item)
        
    def add_tax(self, tax: Tax):
        assert isinstance(tax, Tax)
        self.taxes.append(tax)
        
    def add_payment(self, payment: Payment):
        assert isinstance(payment, Payment)
        self.taxes.append(payment)
        
    def set_merchant(self, merchant: Merchant):
        assert isinstance(merchant, Merchant)
        self.merchant = merchant
