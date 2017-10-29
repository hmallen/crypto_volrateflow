import gdax
import time

product = 'LTC-USD'

public_client = gdax.PublicClient()

for x in range(0, 5):
    product_book = public_client.get_product_order_book(product, level=1)
    high_bid = float(product_book['bids'][0][0])
    low_ask = float(product_book['asks'][0][0])

    product_ticker = public_client.get_product_ticker(product_id=product)
    market_price = float(product_ticker['price'])

    mid_point = (high_bid + low_ask) / 2.0
    offset = market_price - mid_point

    print('BID: ' + str(high_bid))
    print('ASK: ' + str(low_ask))
    print('MID: ' + str(mid_point))
    print('MKT: ' + str(market_price))
    print('OFF: ' + str(offset))
    print()

    time.sleep(5)
