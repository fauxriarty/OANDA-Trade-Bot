import v20
import time
import logging

# Setup logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

# OANDA Configuration
ACCOUNT_ID = '101-001-26879057-001'
ACCESS_TOKEN = '21c00d248066e49bfe89eada01791a10-7f2578ae35b3dacb8ff8acc06c764821'
api = v20.Context('api-fxpractice.oanda.com', '443', token=ACCESS_TOKEN)


def get_last_traded_price(instrument):
    try:
        response = api.pricing.get(ACCOUNT_ID, instruments=instrument)
        price_data = response.get("prices", 200)[0]
        bid = price_data.bids[0].price
        ask = price_data.asks[0].price
        return (bid + ask) / 2
    except Exception as e:
        logging.error(f"Error fetching LTP for {instrument}. Error: {str(e)}")
        return None


def main():
    symbols = ["EUR_USD", "GBP_USD", "USD_JPY"]
    last_prices = {symbol: None for symbol in symbols}

    while True:
        for symbol in symbols:
            current_price = get_last_traded_price(symbol)
            if current_price != last_prices[symbol]:
                print(f"Last traded price for {symbol}: {current_price}")
                last_prices[symbol] = current_price
            time.sleep(10)


if __name__ == "__main__":
    main()
