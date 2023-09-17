import v20
import logging

# Configuration setup
ctx = v20.Context(
    hostname='api-fxpractice.oanda.com',
    port=443,
    token='21c00d248066e49bfe89eada01791a10-7f2578ae35b3dacb8ff8acc06c764821',  # replace with your access token
    # replace with your account ID
)

def get_last_traded_price(instrument):
    response = ctx.pricing.get(
        accountID='101-001-26879057-001',  # replace with your account ID
        instruments=instrument
    )

    if response.status == 200:
        price_data = response.body["prices"][0]
        bid = price_data.bids[0].price
        ask = price_data.asks[0].price
        return (bid + ask) / 2  # return the average of bid and ask as the last traded price
    else:
        logging.error(f"Error fetching LTP for {instrument}. Status Code: {response.status}")
        return None


symbols = ["EUR_USD", "GBP_USD", "USD_JPY"]
for symbol in symbols:
    price = get_last_traded_price(symbol)
    if price:
        print(f"Last traded price for {symbol}: {price}")
