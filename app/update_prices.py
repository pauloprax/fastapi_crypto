import os

from .crud import find_all_active_coin_pair, find_active_coin_pair, update_price_for_coin_pair
from .notification import Notification
from binance import Client


def format_coin(coin):
    return {
        'symbol': coin['symbol'],
        'price': coin['min_price'],
        'max_price': coin['max_price'],
    }


class Prices:
    def __init__(self):
        self.symbols = []
        self.symbols_str = None
        self.api_key = os.environ.get('BINANCE_API_KEY')
        self.api_secret = os.environ.get('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        self.data = None

    async def load(self):
        self.symbols = []
        coins = await find_all_active_coin_pair()
        [self.symbols.append(format_coin(coin)) for coin in coins]
        if len(self.symbols) == 0:
            return
        self.symbols_str = '["' + \
            '","'.join([s['symbol'] for s in self.symbols]) + '"]'
        self.data = self.client.get_symbol_ticker(symbols=self.symbols_str)


class SavePrices:
    def __init__(self, prices):
        self.prices = prices
        self.notifications = []

    async def save(self):
        for s in self.prices.data:
            pair = await find_active_coin_pair(s['symbol'])
            if pair:
                current_price = float(s['price'])
                target_min_price = pair['min_price']
                target_max_price = pair['max_price']
                diff_percentage_to_max_target = 0
                diff_percentage_to_min_target = 0
                if target_max_price is not None:
                    diff_percentage_to_max_target = round((float(current_price) - float(target_max_price))
                                                          / float(target_max_price) * 100, 2)
                    if current_price >= target_max_price:
                        self.notifications.append({
                            'symbol': s['symbol'],
                            'price': current_price,
                            'target_price': target_max_price,
                            'diff_percentage_to_max_target': diff_percentage_to_max_target,
                            'type': 'max'
                        })

                if target_min_price is not None:
                    diff_percentage_to_min_target = round((float(current_price) - float(target_min_price))
                                                          / float(target_min_price) * 100, 2)
                    if current_price <= target_min_price:
                        self.notifications.append({
                            'symbol': s['symbol'],
                            'price': current_price,
                            'target_price': target_min_price,
                            'diff_percentage_to_min_target': diff_percentage_to_min_target,
                            'type': 'min'
                        })

                await update_price_for_coin_pair(pair['_id'], current_price, diff_percentage_to_max_target, diff_percentage_to_min_target)


class SendNotifications:
    def __init__(self, notifications):
        self.notifications = notifications

    async def send(self):
        for notification in self.notifications:
            message = f"Symbol: {notification['symbol']}\n" \
                      f"Current Price: {notification['price']}\n" \
                      f"Target Price: {notification['target_price']}\n" \
                      f"Diff Percentage: {notification['diff_percentage_to_max_target'] if notification['type'] == 'max' else notification['diff_percentage_to_min_target']}\n" \
                      f"Type: {notification['type']}"
            notification = Notification(message)
            notification.send()


async def update_prices_task():
    prices = Prices()
    await prices.load()
    save_prices = SavePrices(prices)
    await save_prices.save()
    send_notifications = SendNotifications(save_prices.notifications)
    await send_notifications.send()
