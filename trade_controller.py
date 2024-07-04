import requests
import urllib.parse
import hashlib
import hmac
import base64
import os
import time
from typing import Optional, Union
from dotenv import load_dotenv, find_dotenv


class TradeController:
    load_dotenv(find_dotenv())
    api_key = os.environ.get("API_KEY")
    api_sec = os.environ.get("API_SECRET")

    def __init__(self, api_key=api_key) -> None:
        self.headers = {
            'API-Key': api_key
        }

    @staticmethod
    def generate_nonce():
        time.sleep(3)
        return int(time.time())

    def get_kraken_signature(self, uripath, data, secret=api_sec):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = uripath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        self.headers['API-Sign'] = sigdigest.decode()

    @staticmethod
    def get_server_time(url="https://api.kraken.com/0/public/Time"):
        return requests.get(url).json()

    @staticmethod
    def get_system_status(url="https://api.kraken.com/0/public/SystemStatus"):
        return requests.get(url).json()

    @staticmethod
    def get_asset_info(assets, url="https://api.kraken.com/0/public/Assets"):
        assets_str = ",".join(assets) if isinstance(assets, list) else assets
        params = {
            'asset': assets_str
        }
        return requests.get(url=url, params=params).json()

    @staticmethod
    def get_tradable_asset_pairs(pairs, url="https://api.kraken.com/0/public/AssetPairs"):
        pairs_str = ",".join(pairs) if isinstance(pairs, list) else pairs
        params = {
            'pair': pairs_str
        }
        return requests.get(url, params=params).json()

    @staticmethod
    def get_ticker_info(pairs: Optional[Union[list, str]], url="https://api.kraken.com/0/public/Ticker"):
        if pairs:
            pairs_str = ",".join(pairs) if isinstance(pairs, list) else pairs
            params = {
                'pair': pairs_str
            }
            return requests.get(url, params=params).json()
        else:
            return requests.get(url).json()

    @staticmethod
    def get_ohlc_data(pair, since, interval=1, url="https://api.kraken.com/0/public/OHLC"):
        params = {
            'pair': pair,
            'interval': interval,
            'since': since
        }
        return requests.get(url, params=params).json()

    @staticmethod
    def get_order_book(pair, count, url="https://api.kraken.com/0/public/Depth"):
        params = {
            "pair": pair,
            "count": count
        }
        return requests.get(url, params=params).json()

    @staticmethod
    def get_recent_trades(pair, since, count=1000, url="https://api.kraken.com/0/public/Trades"):
        params = {
            "pair": pair,
            "since": since,
            "count": count
        }
        return requests.get(url, params=params).json()

    @staticmethod
    def get_recent_spreads(pair, since, url="https://api.kraken.com/0/public/Spread"):
        params = {
            "pair": pair,
            "since": since
        }
        return requests.get(url, params=params).json()

    def get_deposit_methods(self, asset_name, url="https://api.kraken.com/0/private/DepositMethods",
                            uri='/0/private/DepositMethods'):
        params = {
            'nonce': self.generate_nonce(),
            'asset': asset_name
        }
        self.get_kraken_signature(uri, data=params)
        return requests.get(url, headers=self.headers, params=params).json()

    def get_account_balance(self, cash_only=True, url="https://api.kraken.com/0/private/Balance", uri='/0/private/Balance'):
        params = {
            'nonce': self.generate_nonce()
        }
        self.get_kraken_signature(uri, data=params)
        if cash_only:
            return float(requests.post(url, headers=self.headers, data=params).json()['result']['ZUSD'])
        return requests.post(url, headers=self.headers, data=params).json()

    def add_order(self, pair, type, volume, order_type='market', url="https://api.kraken.com/0/private/AddOrder",
                  uri='/0/private/AddOrder'):
        params = {
            'nonce': self.generate_nonce(),
            'pair': pair,
            'ordertype': order_type,
            'type': type,
            'volume': volume,
        }
        self.get_kraken_signature(uri, data=params)
        return requests.post(url, headers=self.headers, data=params).json()
    
    @staticmethod
    def get_server_time(url='https://api.kraken.com/0/public/Time'):
        return requests.get(url).json()['result']['unixtime']
    
    def query_orders(self, txid=None, url="https://api.kraken.com/0/private/QueryOrders", uri='/0/private/QueryOrders'):
        params = {
            'nonce': self.generate_nonce(),
            'txid': txid
        }
        self.get_kraken_signature(uri, data=params)
        return requests.post(url, headers=self.headers, data=params).json()


if __name__ == '__main__':
    trade = TradeController()
    