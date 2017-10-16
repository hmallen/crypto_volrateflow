#!/usr/env python3
# TO DO:
# - Limit deque length to selected time frame
# - Buy/Sell amt. difference at inner point of spread (volume?)

import csv
import datetime
from collections import deque
import gdax
import sys
import time

print()
print('1: BTC-USD')
print('2: LTC-USD')
print('3: ETH-USD')
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

logging_threshold = 1000  # NEED TO INCREASE?
logging_threshold_match = 100  # NEED TO INCREASE?

data_length = 1000  # NEED TO INCREASE?
data_length_match = 100  # NEED TO INCREASE?

buy_data = deque(maxlen=data_length)
sell_data = deque(maxlen=data_length)
match_data = deque(maxlen=data_length_match)

log_datetime_raw = datetime.datetime.now()
log_datetime = log_datetime_raw.strftime('%m%d%Y-%H%M%S')
log_file = 'logs/' + log_datetime + product + '--' + log_datetime + '--volrateflow_log.csv'
#log_file = product + '--' + "{:.2f}".format(log_datetime) + '--' + 'volrateflow_log.csv'
#log_file = 'logs/' + product + '--' + 'volrateflow_log.csv'


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
                order_tot = float(msg["size"]) * float(msg["price"])    # First calculation
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

log_active = False

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
    for x in range(0, buy_length):
        buy_tot = buy_tot + float(buy_data[x][1])
    buy_avg = buy_tot / buy_length
    for x in range(0, sell_length):
        sell_tot = sell_tot + float(sell_data[x][1])
    sell_avg = sell_tot / sell_length
    for x in range(0, match_length):
        match_tot = match_tot + float(match_data[x][1])
    match_avg = match_tot / match_length
    
    time_elapsed_buylist = float((buy_data[buy_length_index][0] - buy_data[0][0]).total_seconds())
    time_elapsed_selllist = float((sell_data[sell_length_index][0] - sell_data[0][0]).total_seconds())
    time_elapsed_matchlist = float((match_data[match_length_index][0] - match_data[0][0]).total_seconds())

    buy_volrateflow = (60.0 * buy_avg) / time_elapsed_buylist
    sell_volrateflow = (60.0 * sell_avg) / time_elapsed_selllist
    buysell_differential = buy_volrateflow - sell_volrateflow
    match_volrateflow = (60.0 * match_avg) / time_elapsed_matchlist
    match_rate = (60.0 * float(match_length)) / time_elapsed_matchlist

    product_book = public_client.get_product_order_book(product, level=1)
    product_ticker = public_client.get_product_ticker(product_id=product)

    high_bid = float(product_book['bids'][0][0])
    high_bid_vol = float(product_book['bids'][0][1])
    high_bid_amt = high_bid * high_bid_vol
    low_ask = float(product_book['asks'][0][0])
    low_ask_vol = float(product_book['asks'][0][1])
    low_ask_amt = low_ask * low_ask_vol
    spread = low_ask - high_bid

    market_price = float(product_ticker['price'])
    day_volume = float(product_ticker['volume'])

    print('----------------------------------------')
    print('buy_length:        ' + "{:}".format(buy_length))
    print('sell_length:       ' + "{:}".format(sell_length))
    print('match_length:      ' + "{:}".format(match_length))
    print()
    print('buy_avg:           $' + "{:.2f}".format(buy_avg))
    print('sell_avg:          $' + "{:.2f}".format(sell_avg))
    if match_avg < 0:
        match_avg_print = abs(match_avg)
        print('match_avg:        -($' + "{:.2f}".format(match_avg_print) + ')')
    elif match_avg >= 0:
        print('match_avg:         $' + "{:.2f}".format(match_avg))
    print()
    
    print('Time (Buy):   ' + "{:.2f}".format(time_elapsed_buylist))
    print('Time (Sell):  ' + "{:.2f}".format(time_elapsed_selllist))
    print('Time (Match): ' + "{:.2f}".format(time_elapsed_matchlist))
    print()
    
    print('VOLUME RATE FLOW')
    print('Buy:               $' + "{:.2f}".format(buy_volrateflow) + ' /min')
    print('Sell:              $' + "{:.2f}".format(sell_volrateflow) + ' /min')
    if buysell_differential < 0:
        buysell_differential_print = abs(buysell_differential)
        print('Differential:     -($' + "{:.2f}".format(buysell_differential_print) + ') /min')
    elif buysell_differential >= 0:
        print('Differential:      $' + "{:.2f}".format(buysell_differential) + ' /min')
    if match_volrateflow < 0:
        match_volrateflow_print = abs(match_volrateflow)
        print('Match:            -($' + "{:.2f}".format(match_volrateflow_print) + ') /min')
    elif match_volrateflow >= 0:
        print('Match:             $' + "{:.2f}".format(match_volrateflow) + ' /min')
    print('Match Rate:        $' + "{:.2f}".format(match_rate) + ' matches/min')
    print()
    
    print('MARKET')
    print('High Bid:           $' + "{:.2f}".format(high_bid) + ' / Total: ' + '$' + "{:.2f}".format(high_bid_amt))
    print('Low Ask:            $' + "{:.2f}".format(low_ask) + ' / Total: ' + '$' + "{:.2f}".format(low_ask_amt))
    print('Spread:             $' + "{:.2f}".format(spread))
    print('Market Price:       $' + "{:.2f}".format(market_price) + ' / 24hr Volume: ' + "{:.2f}".format(day_volume))
    print('----------------------------------------')
    print()

    if log_active == False:
        if buy_length >= logging_threshold and sell_length >= logging_threshold and match_length >= logging_threshold_match:
            log_active = True
            print('Logging activated.')
            print()

    """
    Logging:
    1-Date/Time, 2-Buy VRF, 3-Sell VRF,
    4-Buy/Sell Differential, 5-Match VRF, 6-Match Rate,
    7-High Bid, 8-High Bid Volume, 9-High Bid Amount,
    10-Low Ask, 11-Low Ask Volume, 12-Low Ask Amount,
    13-Spread, 14-Market Price, 15-24hr Volume
    """
    if log_active == True:
        with open(log_file, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([datetime.datetime.now(), "{:.2f}".format(buy_volrateflow), "{:.2f}".format(sell_volrateflow), "{:.2f}".format(buysell_differential),
                                 "{:.2f}".format(match_volrateflow), "{:.2f}".format(match_rate), "{:.2f}".format(high_bid), "{:.2f}".format(high_bid_vol), "{:.2f}".format(high_bid_amt),
                                 "{:.2f}".format(low_ask), "{:.2f}".format(low_ask_vol), "{:.2f}".format(low_ask_amt), "{:.2f}".format(spread), "{:.2f}".format(market_price), "{:.2f}".format(day_volume)])
    
    time.sleep(10)

"""   
finally:
    wsClient.close()
    print('Websocket closed.')
"""
