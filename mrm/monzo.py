import requests
import datetime
import json
import os

class APIResponse:
    
    def __init__(self, r, key: str = None):
        self.r = r
        self.status = self.r.status_code
        self.ok = self.r.status_code == requests.codes.ok
        try:
            self.data = self.r.json().get(key, self.r.json())
        except:
            self.data = self.r.text
    
    def __bool__(self):
        return self.ok
    
    def __repr__(self):
        return self.r.__repr__()


class Monzo:
    
    
    def __init__(self):
        self.client_id = os.environ['MONZO_CLIENT_ID']
        self.client_secret = os.environ['MONZO_CLIENT_SECRET']
        self.token = json.loads(os.environ['MONZO_TOKEN'])
    
    def _build_headers(self, **kwargs):
        kwargs['Authorization'] = "Bearer " + self.token.get('access_token')
        return kwargs
    
    def _build_url(self, *args):
        _url = 'https://api.monzo.com/'
        _url += '/'.join(args)
        _url += '/'
        return _url
    
    
    def list_accounts(self):
        url = self._build_url('accounts')
        method = 'GET'
        headers = self._build_headers()
        r = requests.request(method, url, headers=headers)
        return APIResponse(r, 'accounts')
    
    
    def read_balance(self, account_id: str):
        url = self._build_url('balance')
        method = 'GET'
        headers = self._build_headers()
        params = {'account_id': account_id}
        r = requests.request(method, url, headers=headers, params=params)
        return APIResponse(r)
    
    
    def list_pots(self, account_id: str):
        url = self._build_url('pots')
        method = 'GET'
        headers = self._build_headers()
        params = {'current_account_id': account_id}
        r = requests.request(method, url, headers=headers, params=params)
        return APIResponse(r, 'pots')
    
    
    def pot_deposit(self, pot_id: str, account_id: str, amount: int, snowflake: str):
        url = self._build_url('pots', pot_id, 'deposit')
        method = 'PUT'
        headers = self._build_headers()
        data = {'source_account_id': account_id, 'amount': amount, 'dedupe_id': snowflake}
        r = requests.request(method, url, headers=headers, data=data)
        return APIResponse(r)
    
    
    def pot_withdraw(self, pot_id: str, account_id: str, amount: int, snowflake: str):
        url = self._build_url('pots', pot_id, 'withdraw')
        method = 'PUT'
        headers = self._build_headers()
        data = {'source_account_id': account_id, 'amount': amount, 'dedupe_id': snowflake}
        r = requests.request(method, url, headers=headers, data=data)
        return APIResponse(r)
    
    
    def get_transaction(self, transaction_id: str):
        url = self._build_url('transactions', transaction_id)
        method = 'GET'
        headers = self._build_headers(**{'expand[]': 'merchant'})
        r = requests.request(method, url, headers=headers)
        return APIResponse(r, 'transaction')
    
    
    def list_transactions(self,
        account_id: str,
        since: datetime.datetime = None,
        before: datetime.datetime = None,
    ):
        url = self._build_url('transactions')
        method = 'GET'
        if since is None:
            since = (
                datetime.datetime.utcnow().astimezone()-datetime.timedelta(days=7)
                )
        if before is None:
            before = datetime.datetime.utcnow().astimezone()
        headers = self._build_headers()
        params = {
            'account_id': account_id,
            'since': since.isoformat(),
            'before': before.isoformat()
        }
        print(f"Loading transactions between {since} and {before}")
        r = requests.request(method, url, headers=headers, params=params)
        return APIResponse(r, 'transactions')
    
    
    def annotate_transaction(self, transaction_id: str, **kwargs):
        url = self._build_url('transactions', transaction_id)
        method = 'PATCH'
        headers = self._build_headers(**{'expand[]': 'merchant'})
        data = {f'metadata[{x}]': y for x, y in kwargs.items()}
        r = requests.request(method, url, headers=headers, data=data)
        return APIResponse(r, 'transaction')


    def create_reciept(self, reciept: dict):
        url = self._build_url('transaction-receipts')
        method = 'PUT'
        headers = self._build_headers()
        r = requests.request(method, url, headers=headers, json=reciept)
        return APIResponse(r)


    def get_reciept(self, receipt_id: str):
        url = self._build_url('transaction-receipts')
        method = 'GET'
        headers = self._build_headers()
        params = {
            'external_id': receipt_id,
        }
        r = requests.request(method, url, headers=headers, params=params)
        return APIResponse(r, 'receipt')


    def delete_reciept(self, receipt_id: str):
        url = self._build_url('transaction-receipts')
        method = 'DELETE'
        headers = self._build_headers()
        params = {
            'external_id': receipt_id,
        }
        r = requests.request(method, url, headers=headers, params=params)
        return APIResponse(r)
    
    def create_reciept_and_associate(self, reciept: dict):
        receipt_id = reciept.get('external_id')
        transaction_id = reciept.get('transaction_id')
        receipt = self.create_reciept(reciept)
        transaction = None
        if receipt:
            transaction = self.annotate_transaction(transaction_id, receipt_id=receipt_id)
        return (reciept, transaction)
