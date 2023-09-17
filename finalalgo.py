import v20
import time
import threading

ACCESS_TOKEN = '21c00d248066e49bfe89eada01791a10-7f2578ae35b3dacb8ff8acc06c764821'
ACCOUNT_ID = '101-001-26879057-001'
api = v20.Context('api-fxpractice.oanda.com', '443', token=ACCESS_TOKEN)


ltp_cache = {} #to store the ltp in a dictionary
orb_cache = {} #dict to store the opening range breakout values
order_cache = set() #to make sure same order isnt placed multiple times

#to fetch the last traded price for a symbol
def get_last_traded_price(instrument):
    response = api.pricing.get(ACCOUNT_ID, instruments=instrument)
    if response.status == 200:
        price_data = response.get("prices", 200)[0]
        return price_data.bids[0].price
    return None

# to fetch the ORB for a symbol
def fetch_orb(instrument):
    params = {
        "count": 2, #number of candles to fetch
        "granularity": "M15" #candle duration (15 minutes as specified for the project)
    }
    response = api.instrument.candles(instrument, **params)
    if response.status == 200:
        candles = response.get("candles", 200)
        high = max([candle.mid.h for candle in candles])
        low = min([candle.mid.l for candle in candles])
        return (high, low)
    return None, None

#to generate a signal to buy or sell based on the orb and ltp fetched
def generate_signal(symbol):
    ltp = get_last_traded_price(symbol)
    high, low = orb_cache.get(symbol, (None, None))

    if not ltp or not high or not low:
        return None

    if ltp > high:
        return "BUY"
    elif ltp < low:
        return "SELL"
    return None

#to place an order based on the signal
def place_order(symbol, signal):
    # to check if order already placed
    order_key = f"{symbol}_{signal}"
    if order_key in order_cache:
        return

    order = {
        "order": {
            "instrument": symbol,
            "units": 50 if signal == "BUY" else -50, #buy 50 units if signal buy otherwise sell 50
            "type": "MARKET",
            "timeInForce": "FOK" #it means order will either be fully executed or fully denied
        }
    }

    #placing the order
    response = api.order.create(ACCOUNT_ID, **order)
    if response.status == 201:
        order_cache.add(order_key)
        print(f"Order placed: {order_key}")
        print(response.body)  # printing the entire response for debugging
        if 'orderCancelTransaction' in response.body: #in case order was cancelled find out why for debugging
            cancel_transaction = response.body['orderCancelTransaction']
            print(f"Order for {symbol} was canceled. Reason: {cancel_transaction.reason}")

    else:
        print(f"Failed to place order for {symbol}. Status code: {response.status}")
        print(response.body)  # Print the entire response for debugging


def threaded_task(symbol): #to continously generate signals and place orders for a symbol as a thread
    while True:
        orb_cache[symbol] = fetch_orb(symbol)
        signal = generate_signal(symbol)
        if signal:
            place_order(symbol, signal)
        time.sleep(10)  # checks every 10 seconds for a signal

def main():
    symbols = ["EUR_USD", "GBP_USD", "USD_JPY"]
    threads = []

    #to start a separate thread for each symbol
    for symbol in symbols:
        t = threading.Thread(target=threaded_task, args=(symbol,))
        t.start()
        threads.append(t)

    for t in threads: #once all threads completed
        t.join()


if __name__ == "__main__":
    main()
