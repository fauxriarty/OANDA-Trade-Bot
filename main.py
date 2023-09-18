import v20
import time
import threading

class TradingBot:
    def __init__(self, access_token, account_id):
        self.api = v20.Context('api-fxpractice.oanda.com', '443', token=access_token)
        self.account_id = account_id

        self.ltp_cache = {}  # to store the ltp in a dictionary
        self.orb_cache = {}  # dict to store the opening range breakout values
        self.order_cache = set()  # to make sure the same order isn't placed multiple times

    def get_last_traded_price(self, instrument):
        response = self.api.pricing.get(self.account_id, instruments=instrument)
        if response.status == 200:
            price_data = response.get("prices", 200)[0]
            return price_data.bids[0].price
        return None

    def fetch_orb(self, instrument):
        params = {
            "count": 2,  # number of candles to fetch
            "granularity": "M15"  # candle duration (15 minutes as specified for the project)
        }
        response = self.api.instrument.candles(instrument, **params)
        if response.status == 200:
            candles = response.get("candles", 200)
            high = max([candle.mid.h for candle in candles])
            low = min([candle.mid.l for candle in candles])
            return (high, low)
        return None, None

    def generate_signal(self, symbol):
        ltp = self.get_last_traded_price(symbol)
        high, low = self.orb_cache.get(symbol, (None, None))

        if not ltp or not high or not low:
            return None

        if ltp > high:
            return "BUY"
        elif ltp < low:
            return "SELL"
        return None

    def place_order(self, symbol, signal):
        order_key = f"{symbol}_{signal}"
        if order_key in self.order_cache:
            return

        order = {
            "order": {
                "instrument": symbol,
                "units": 50 if signal == "BUY" else -50,  # buy 50 units if signal buy otherwise sell 50
                "type": "MARKET",
                "timeInForce": "FOK"  # it means order will either be fully executed or fully denied
            }
        }

        response = self.api.order.create(self.account_id, **order)
        if response.status == 201:
            self.order_cache.add(order_key)
            print(f"Order placed: {order_key}")
            print(response.body)  # printing the entire response for debugging
            if 'orderCancelTransaction' in response.body:  # in case order was cancelled find out why for debugging
                cancel_transaction = response.body['orderCancelTransaction']
                print(f"Order for {symbol} was canceled. Reason: {cancel_transaction.reason}")
        else:
            print(f"Failed to place order for {symbol}. Status code: {response.status}")
            print(response.body)

    def threaded_task(self, symbol):
        while True:
            self.orb_cache[symbol] = self.fetch_orb(symbol)
            signal = self.generate_signal(symbol)
            if signal:
                self.place_order(symbol, signal)
            time.sleep(15)  # checks every 15 seconds for a signal

    def run(self):
        symbols = ["EUR_USD", "GBP_USD", "USD_JPY"]
        threads = []

        for symbol in symbols:
            t = threading.Thread(target=self.threaded_task, args=(symbol,))
            t.start()
            threads.append(t)

        for t in threads:  # once all threads completed
            t.join()


if __name__ == "__main__":
    ACCESS_TOKEN = '21c00d248066e49bfe89eada01791a10-7f2578ae35b3dacb8ff8acc06c764821'
    ACCOUNT_ID = '101-001-26879057-001'
    bot = TradingBot(ACCESS_TOKEN, ACCOUNT_ID)
    bot.run()
