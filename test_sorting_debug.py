#!/usr/env python3
# TO DO:
# - Limit deque length to selected time frame

import csv
import datetime
from collections import deque
import gdax
import sys
import time

print()
print('1 - BTC')
print('2 - LTC')
print('3 - ETH')
print()

user_product = input('Choose Product: ')
if user_product == '1':
    product = 'BTC-USD'
    print('BTC-USD market selected.')
elif user_product == '2':
    product = 'LTC-USD'
    print('LTC-USD market selected.')
elif user_product == '3':
    product = 'ETH-USD'
    print('ETH-USD market selected.')
else:
    print('Incorrect selection. Exiting')
    sys.exit(0)
print()

data_length = 1000
data_length_match = 100

buy_data = deque(maxlen=data_length)
sell_data = deque(maxlen=data_length)
match_data = deque(maxlen=data_length_match)

log_datetime = datetime.datetime.now()
log_file = product + '--' + log_datetime + '--' + 'volrateflow_log.csv'


class myWebsocketClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = [product]
        self.message_count = 0
        self.deque_count = 0
    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            msg_time = datetime.datetime.now()
            msg_type = msg["type"]
            msg_side = msg["side"]
            
            if msg_type == 'received':
                order_tot = float(msg["size"]) * float(msg["price"])
                if msg_side == 'buy':
                    buy_data.append((msg_time, order_tot))
                elif msg_side == 'sell':
                    sell_data.append((msg_time, order_tot))
            elif msg_type == 'done' and msg["reason"] == 'cancelled':
                order_tot = -1.0 * (float(msg["size"]) * float(msg["price"]))
                if msg_side == 'buy':
                    buy_data.append((msg_time, order_tot))
                elif msg_side == 'sell':
                    sell_data.append((msg_time, order_tot))
            elif msg_type == 'match':
                order_tot = float(msg["size"]) * float(msg["price"])
                if msg_side == 'buy':
                    match_data.append((msg_time, order_tot))
                elif msg_side == 'sell':
                    match_data.append((msg_time, (-1.0 * order_tot)))
            elif msg_type == 'change':
                order_tot = float(msg["size"]) * float(msg["price"])
                print('---- CHANGE ----')
    def on_close(self):
        print('Closing websocket.')


public_client = gdax.PublicClient()

wsClient = myWebsocketClient()
wsClient.start()

print(wsClient.url, wsClient.products)

print('Accumulating market data. Please wait...')
while (wsClient.message_count < 1000):
    time.sleep(1)

print('Beginning analysis.')
print()
while (True):
    buy_length = len(buy_data)
    buy_length_index = buy_length - 1
    sell_length = len(sell_data)
    sell_length_index = sell_length - 1
    match_length = len(match_data)
    match_length_index = match_length - 1
    
    if match_length == 0:
        match_length_index = 0
    else:
        match_length_index = match_length - 1

    buy_tot = 0.0
    sell_tot = 0.0
    match_tot = 0.0
    for x in range(0, buy_length_index):
        buy_tot = buy_tot + float(buy_data[x][1])
    buy_avg = buy_tot / buy_length
    for x in range(0, sell_length_index):
        sell_tot = sell_tot + float(sell_data[x][1])
    sell_avg = sell_tot / sell_length
    for x in range(0, match_length_index):
        match_tot = match_tot + float(match_data[x][1])
    match_avg = match_tot / match_length
    
    time_elapsed_buy = float((buy_data[buy_length_index][0] - buy_data[0][0]).total_seconds())
    time_elapsed_sell = float((sell_data[sell_length_index][0] - sell_data[0][0]).total_seconds())
    time_elapsed_match = float((match_data[match_length_index][0] - match_data[0][0]).total_seconds())

    buy_volrateflow = (60.0 * buy_avg) / time_elapsed_buy
    sell_volrateflow = (60.0 * sell_avg) / time_elapsed_sell
    buysell_differential = buy_volrateflow - sell_volrateflow
    match_volrateflow = (60.0 * match_avg) / time_elapsed_match
    match_rate = (60.0 * float(match_length)) / time_elapsed_match

    product_book = public_client.get_product_order_book(product, level=1)
    product_ticker = public_client.get_product_ticker(product_id=product)

    high_bid = float(product_book['bids'][0][0])
    high_bid_vol = float(product_book['bids'][0][1])
    high_bid_amt = high_bid * high_bid_vol
    low_ask = float(product_book['asks'][0][0])
    low_ask_vol = float(product_book['asks'][0][1])
    low_ask_amt = low_ask * low_ask_vol

    market_price = float(product_ticker['price'])
    day_volume = float(product_ticker['volume'])

    print('----------------------------------------')
    print('buy_length:   ' + str(buy_length))
    print('sell_length:  ' + str(sell_length))
    print('match_length: ' + str(match_length))
    print('match_avg:    ' + str(match_avg))
    print('match_tot:    ' + str(match_tot))
    print('match_length: ' + str(match_length))
    print()
    print('buy_avg:   ' + str(buy_avg))
    print('sell_avg:  ' + str(sell_avg))
    print('match_avg: ' + str(match_avg))
    print()
    print('time_elapsed_buy:   ' + str(time_elapsed_buy))
    print('time_elapsed_sell:  ' + str(time_elapsed_sell))
    print('time_elapsed_match: ' + str(time_elapsed_match))
    print()
    print('VOLUME RATE FLOW')
    print('Buy:          ' + str(buy_volrateflow) + ' $/min')
    print('Sell:         ' + str(sell_volrateflow) + ' $/min')
    print('Differential: ' + str(buysell_differential) + ' $/min')
    print('Match:        ' + str(match_volrateflow) + ' $/min')
    print('Match Rate:   ' + str(match_rate) + ' matches/min')
    print()
    print('MARKET')
    print('High Bid:     ' + str(high_bid) + ' / Total: ' + '$' + str(high_bid_amt))
    print('Low Ask:      ' + str(low_ask) + ' / Total: ' + '$' + str(low_ask_amt))
    print('Market Price: ' + str(market_price) + ' / 24hr Volume: ' + str(day_volume))
    print('----------------------------------------')
    print()

    with open(log_file, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([datetime.datetime.now(), "{:.2f}".format(buy_volrateflow), "{:.2f}".format(sell_volrateflow), "{:.2f}".format(buysell_differential),
                             "{:.2f}".format(match_volrateflow), "{:.2f}".format(match_rate), "{:.2f}".format(high_bid), "{:.2f}".format(high_bid_vol), "{:.2f}".format(high_bid_amt),
                             "{:.2f}".format(low_ask), "{:.2f}".format(low_ask_vol), "{:.2f}".format(low_ask_amt), "{:.2f}".format(market_price), "{:.2f}".format(day_volume)])
    
    time.sleep(10)

"""   
finally:
    wsClient.close()
    print('Websocket closed.')
"""
