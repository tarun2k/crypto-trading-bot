from trade_controller import TradeController
from kraken_wsclient_py import WssClient as WsClient
import pandas as pd


class BollingerBandTrade:

    def __init__(self, window_size):
        self.controller = TradeController()
        self.universe = self.controller.get_ticker_info(None)
        self.coarse = None
        self.fine = None
        self.channel_mapping = {}
        self.bands = None
        self.window_size = window_size
        self.cash_amount = self.controller.get_account_balance()
        self.cash_allocation = 0
        self.open_positions = {}

    def coarse_selection(self, criterion='v', sample_size=50):
        coarse = [(k, v) for k, v in self.universe['result'].items() if k[-3:] == 'USD']
        coarse.sort(key=lambda x: x[1][criterion][0], reverse=True)
        self.coarse = coarse[:sample_size]

    def fine_selection(self, criterion='t', sample_size=10):
        fine = self.coarse
        fine.sort(key=lambda x: x[1][criterion][0], reverse=True)
        self.fine = [pair for pair, _ in fine][:sample_size]

    def prepare_execution(self):
        pair_info = self.controller.get_tradable_asset_pairs(self.fine)['result']
        self.fine = [val['wsname'] for _, val in pair_info.items()]
        self.cash_allocation = self.cash_amount / len(self.fine)
        print(self.fine)

        self.bands = {pair: pd.DataFrame({
            'price': []
        }) for pair in self.fine}

    def update_bands(self, pair):
        self.bands[pair]['sma'] = self.bands[pair]['price'].rolling(window=self.window_size).mean()
        self.bands[pair]['std'] = self.bands[pair]['price'].rolling(window=self.window_size).std()
        self.bands[pair]['upper band'] = self.bands[pair]['sma'] + 2 * self.bands[pair]['std']
        self.bands[pair]['lower band'] = self.bands[pair]['sma'] - 2 * self.bands[pair]['std']

        if len(self.bands[pair]) > self.window_size:
            self.bands[pair] = self.bands[pair].tail(self.window_size)

    def execute_trade(self, pair, volume):
        if self.bands[pair]['upper band'].iloc[-1] and self.bands[pair]['lower band'].iloc[-1]:
            if self.bands[pair]['price'].iloc[-1] < self.bands[pair]['lower band'].iloc[-1]:
                if pair not in self.open_positions:
                    self.controller.add_order(pair, 'buy', self.bands[pair]['lower band'].iloc[-1], volume)
                    self.open_positions[pair] = 'buy'
                    print(f"{pair} buy order placed")
            elif self.bands[pair]['price'].iloc[-1] > self.bands[pair]['upper band'].iloc[-1]:
                if pair in self.open_positions:
                    if self.open_positions[pair] == 'buy':
                        self.controller.add_order(pair, 'sell', self.bands[pair]['upper band'].iloc[-1], volume)
                        self.open_positions[pair] = 'sell'
                        print(f"{pair} sell order placed")

    def websocket_handler(self, message):
        if isinstance(message, dict) and 'channelID' in message.keys() and 'pair' in message.keys():
            self.channel_mapping[message['channelID']] = str(message['pair'])

        elif isinstance(message, list):
            pair_name = self.channel_mapping[message[0]]
            last_price = float(message[1]['c'][0])
            self.bands[pair_name] = pd.concat([self.bands[pair_name], pd.DataFrame({'price': [last_price]})],
                                              ignore_index=True)
            volume = self.cash_allocation / last_price
            self.update_bands(pair_name)
            print(pair_name)
            print(self.bands[pair_name])
            self.execute_trade(pair_name, volume)

    def websocket_start(self):
        my_client = WsClient()
        my_client.start()

        my_client.subscribe_public(
            subscription={
                'name': 'ticker'
            },
            pair=self.fine,
            callback=self.websocket_handler
        )

    def execute(self):
        self.coarse_selection()
        self.fine_selection()
        self.prepare_execution()
        self.websocket_start()
