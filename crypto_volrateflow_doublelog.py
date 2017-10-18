#!/usr/env python3

# TO DO:
# - Log multiple time intervals (multiple files) for testing
# - Add buy rate/sell rate (RELATIVE TO 24HR VOLUME?)
# - Plot long interval vs. short interval and look for crossover?
# - NEED TO FIX WHOLE SECTION STARTING ON LINE 272
# - NEED TO SPLIT INTO MULTIPLE LOGS
# - NEED TO MAKE WEIGHTED AVERAGES
# - NEED TO ADD NEW AVERAGES TO DISPLAY_DATA()
# - Remove formatting from csv write (full float precision)

import csv
import datetime
from collections import deque
import gdax
import os
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

# Setup timedelta for short backtesting interval
print('Please input desired backtesting time. (SHORT Duration)')
user_interval_short_raw = input('Interval (min): ')
try:
    user_interval_short = int(user_interval_short_raw)
    delta_interval_short = datetime.timedelta(minutes=user_interval_short)
    time_start = datetime.datetime.now()
    if user_interval_short == 1:
        print('Using short backtesting interval of 1 minute.')
    else:
        print('Using short backtesting interval of ' + "{}".format(user_interval_short) + ' minutes.')
    print()
except:
    print('Invalid input. Exiting.')

# Setup timedelta for long backtesting interval
print('Please input desired backtesting time. (LONG Duration)')
user_interval_long_raw = input('Interval (min): ')
try:
    user_interval_long = int(user_interval_long_raw)
    delta_interval_long = datetime.timedelta(minutes=user_interval_long)
    time_start = datetime.datetime.now()
    if user_interval_long == 1:
        print('Using short backtesting interval of 1 minute.')
    else:
        print('Using short backtesting interval of ' + "{}".format(user_interval_long) + ' minutes.')
        print()
except:
    print('Invalid input. Exiting.')

# MAKE RELATIVE TO USER INPUT????
data_length = 20000  # NEED TO INCREASE?
data_length_match = 1000  # NEED TO INCREASE?

buy_data = deque(maxlen=data_length)
sell_data = deque(maxlen=data_length)
match_data = deque(maxlen=data_length_match)

if not os.path.exists('logs'):
    os.makedirs('logs')
log_datetime_raw = datetime.datetime.now()
log_datetime = log_datetime_raw.strftime('%m%d%Y-%H%M%S')
log_file_short = 'logs/' + log_datetime + product + '--' + log_datetime + '--volrateflow_log_SHORT.csv'
log_file_long = 'logs/' + log_datetime + product + '--' + log_datetime + '--volrateflow_log_LONG.csv'


class myWebsocketClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = [product]
        self.message_count = 0
        self.buy_count = 0
        self.sell_count = 0
        self.match_count = 0
    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            msg_time = datetime.datetime.now()
            msg_type = msg["type"]
            msg_side = msg["side"]
            
            if msg_type == 'received':
                order_size = float(msg["size"])
                order_price = float(msg["price"])
                order_tot = order_size * order_price
                if msg_side == 'buy':
                    buy_data.append((msg_time, order_tot, order_size, order_price))
                    self.buy_count += 1
                elif msg_side == 'sell':
                    sell_data.append((msg_time, order_tot, order_size, order_price))
                    self.sell_count +=1
            elif msg_type == 'done' and msg["reason"] == 'cancelled':
                order_size = float(msg["size"])
                order_price = float(msg["price"])
                order_tot = -1.0 * order_size * order_price
                if msg_side == 'buy':
                    buy_data.append((msg_time, order_tot, order_size, order_price))
                    self.buy_count += 1
                elif msg_side == 'sell':
                    sell_data.append((msg_time, order_tot, order_size, order_price))
                    self.sell_count += 1
            elif msg_type == 'match':
                order_size = float(msg["size"])
                order_price = float(msg["price"])
                order_tot = order_size * order_price
                if msg_side == 'buy':
                    match_data.append((msg_time, order_tot, order_size, order_price))
                    self.match_count += 1
                elif msg_side == 'sell':
                    match_data.append((msg_time, (-1.0 * order_tot), order_size, order_price))
                    self.match_count += 1
            elif msg_type == 'change':
                order_size = float(msg["size"])
                order_price = float(msg["price"])
                order_tot = order_size * order_price
                print('---- CHANGE ----')
    def on_close(self):
        print('Closing websocket.')


def display_data(debug): # NEED TO UPDATE WITH NEW VARIABLES
    if debug == True:
        print('----------------------------------------')
        print('SHORT INTERVAL')
        print('Buy Length:        ' + "{:}".format(buy_length))
        print('Sell Length:       ' + "{:}".format(sell_length))
        print('Match Length:      ' + "{:}".format(match_length))
        print()
        print('Buy Average:       $' + "{:.2f}".format(buy_avg))
        print('Sell Average:      $' + "{:.2f}".format(sell_avg))
        if match_avg < 0:
            match_avg_print = abs(match_avg)
            print('Match Average:   -($' + "{:.2f}".format(match_avg_print) + ')')
        elif match_avg >= 0:
            print('Match Average:     $' + "{:.2f}".format(match_avg))
        # NEED WEIGHTED AVERAGES HERE
        print()
        
        print('Buy Time:          ' + "{:.2f}".format(time_elapsed_buylist) + ' sec')
        print('Sell Time:         ' + "{:.2f}".format(time_elapsed_selllist) + ' sec')
        print('Match Time:        ' + "{:.2f}".format(time_elapsed_matchlist) + ' sec')
        print()
        
        print('VOLUME RATE FLOW')
        print('Buy:               $' + "{:.2f}".format(buy_volrateflow) + ' /min')
        print('Sell:              $' + "{:.2f}".format(sell_volrateflow) + ' /min')
        if buysell_differential < 0:
            buysell_differential_print = abs(buysell_differential)
            print('Differential:    -($' + "{:.2f}".format(buysell_differential_print) + ') /min')
        elif buysell_differential >= 0:
            print('Differential:      $' + "{:.2f}".format(buysell_differential) + ' /min')
        if match_volrateflow < 0:
            match_volrateflow_print = abs(match_volrateflow)
            print('Match:           -($' + "{:.2f}".format(match_volrateflow_print) + ') /min')
        elif match_volrateflow >= 0:
            print('Match:             $' + "{:.2f}".format(match_volrateflow) + ' /min')
        print('Match Rate:        ' + "{:.2f}".format(match_rate) + ' matches/min')
        print()
    
        print('MARKET')
        print('Low Ask:           $' + "{:.2f}".format(low_ask) + ' -- ' + "{:.2f}".format(low_ask_vol) + ' -- ' + 'Total: $' + "{:.2f}".format(low_ask_amt))
        print('High Bid:          $' + "{:.2f}".format(high_bid) + ' -- ' + "{:.2f}".format(high_bid_vol) + ' -- ' + 'Total: $' + "{:.2f}".format(high_bid_amt))
        print('Market Price:      $' + "{:.2f}".format(market_price) + ' -- ($' + "{:.2f}".format(spread) + ') -- 24hr Volume: ' + "{:.2f}".format(day_volume))
        print('----------------------------------------')
        print()


public_client = gdax.PublicClient()

wsClient = myWebsocketClient()
wsClient.start()

print(wsClient.url, wsClient.products)

log_active = False

print('Accumulating market data. Please wait...')
while (True):
    if wsClient.buy_count > 10 and wsClient.sell_count > 10 and wsClient.match_count > 10:
        print('Data lists populated. Beginning analysis.')
        break

print('Logging will start when backtesting interval reached.')
print()

while (True):
    # Buy Variables
    buy_length = len(buy_data)
    buy_length_index = buy_length - 1
    buy_data_short = deque(maxlen=data_length)
    buy_data_long = deque(maxlen=data_length)
    time_end_buy_short = buy_data[buy_length_index][0] - delta_interval_short
    time_end_buy_long = buy_data[buy_length_index][0] - delta_interval_long

    # Sell Variables
    sell_length = len(sell_data)
    sell_length_index = sell_length - 1
    sell_data_short = deque(maxlen=data_length)
    sell_data_long = deque(maxlen=data_length)
    time_end_sell_short = sell_data[sell_length_index][0] - delta_interval_short
    time_end_sell_long = sell_data[sell_length_index][0] - delta_interval_long

    # Match Variables
    match_data_short = deque(maxlen=data_length_match)
    match_data_long = deque(maxlen=data_length_match)
    match_length = len(match_data)
    match_length_index = match_length - 1
    time_end_match_short = match_data[match_length_index][0] - delta_interval_short
    time_end_match_long = match_data[match_length_index][0] - delta_interval_long

    buy_end_point = 0
    buy_tot = 0.0
    for x in range(buy_length_index, 0, -1):
        if buy_data[x][0] >= time_end_buy_short:
            buy_data_short.append(buy_data[x])
            buy_data_long.append(buy_data[x])
            buy_end_point = x
        elif time_end_buy_short < buy_data[buy_end_point][0] <= time_end_buy_long:
            buy_data_long.append(buy_data[x])
        else:
            break
    buy_selected_length_long = len(buy_data_selected_long)
    buy_selected_index_long = buy_selected_length_long - 1
    buy_selected_length_short = len(buy_data_selected_short)
    buy_selected_index_short = buy_selected_length_short - 1

    sell_end_point = 0
    sell_tot = 0.0
    for x in range(sell_length_index, 0, -1):
        if sell_data[x][0] >= time_end_sell_short:
            sell_data_short.append(sell_data[x])
            sell_data_long.append(sell_data[x])
            sell_end_point = x
        elif time_end_sell_short < sell_data[sell_end_point][0] <= time_end_sell_long:
            sell_data_long.append(sell_data[x])
        else:
            break
    sell_selected_length_long = len(sell_data_selected_long)
    sell_selected_index_long = sell_selected_length_long - 1
    sell_selected_length_short = len(sell_data_selected_short)
    sell_selected_index_short = sell_selected_length_short - 1

    match_end_point = 0
    for x in range(match_length_index, 0, -1):
        if match_data[x][0] >= time_end_match_short:
            match_data_short.append(match_data[x])
            match_data_long.append(match_data[x])
            match_end_point = x
        elif time_end_match_short < match_data[match_end_point][0] <= time_end_match_long:
            match_data_long.append(match_data[x])
    match_selected_length_long = len(match_data_selected_long)
    match_selected_index_long = match_selected_length_long - 1
    match_selected_length_short = len(match_data_selected_short)
    match_selected_index_short = match_selected_length_short - 1

    buy_tot = 0.0
    for x in range(0, buy_selected_length_short):
        buy_tot = buy_tot + float(buy_data_short[x][1])
    buy_avg_short = buy_tot / buy_selected_length_short
    buy_tot = 0.0
    for x in range(0, buy_selected_length_long):
        buy_tot = buy_tot + float(buy_data_long[x][1])
    buy_avg_long = buy_tot / buy_selected_length_long

    sell_tot = 0.0
    for x in range(0, sell_selected_length_short):
        sell_tot = sell_tot + float(sell_data_short[x][1])
    sell_avg_short = sell_tot / sell_selected_length_short
    sell_tot = 0.0
    for x in range(0, sell_selected_length_long):
        sell_tot = sell_tot + float(sell_data_long[x][1])
    sell_avg_long = sell_tot / sell_selected_length_long

    match_tot = 0.0
    for x in range(0, match_selected_length_short):
        match_tot = match_tot + float(match_data_short[x][1])
    match_avg_short = match_tot / match_selected_length_short
    match_tot = 0.0
    for x in range(0, match_selected_length_long):
        match_tot = match_tot + float(match_data_long[x][1])
    match_avg_long = match_tot / match_selected_length_long

    time_elapsed_buylist = float((buy_data[buy_length_index][0] - buy_data[0][0]).total_seconds())
    time_elapsed_selllist = float((sell_data[sell_length_index][0] - sell_data[0][0]).total_seconds())
    time_elapsed_matchlist = float((match_data[match_length_index][0] - match_data[0][0]).total_seconds())

    # THIS WAS TOTALLY WRONG IN PREVIOUS VERSIONS. SHOULDN'T HAVE DIVIDED BY TIME FOR UNTRUNCATED BUY LIST.
    buy_volrateflow_short = (60.0 * buy_avg_short) / float(user_interval_short)
    buy_volrateflow_long = (60.0 * buy_avg_long) / float(user_interval_long)
    sell_volrateflow_short = (60.0 * sell_avg_short) / float(user_interval_short)
    sell_volrateflow_long = (60.0 * sell_avg_long) / float(user_interval_long)
    buysell_differential_short = buy_volrateflow_short - sell_volrateflow_short
    buysell_differential_long = buy_volrateflow_long - sell_volrateflow_long
    match_volrateflow_short = (60.0 * match_avg_short) / float(user_interval_short)
    match_volrateflow_long = (60.0 * match_avg_long) / float(user_interval_long)
    match_rate_short = (60.0 * float(match_length_short)) / float(time_elapsed_matchlist)
    match_rate_long = (60.0 * float(match_length_long)) / float(time_elapsed_matchlist)

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

    display_data()

    if log_active == False:
        # Wait until sufficient quantity of data points collected
        print('Waiting for sufficient data for backtesting.')
        # Wait to collect data for user selected duration before beginning
        time_elapsed_buylist_min = time_elapsed_buylist / 60.0
        time_elapsed_selllist_min = time_elapsed_selllist / 60.0
        time_elapsed_matchlist_min = time_elapsed_matchlist / 60.0
        #if datetime.datetime.now() >= (time_start + delta_interval):  # Wait for extra minute?
        if time_elapsed_buylist_min >= float(user_interval) and time_elapsed_selllist_min >= float(user_interval) and time_elapsed_matchlist_min >= float(user_interval):
            log_active = True
            print('Backtesting interval duration reached. Logging activated.')
        print()
    
    # Logging:
    # 1-Date/Time, 2-Backtesting Interval, 3-Buy VRF, 4-Sell VRF,
    # 5-Buy/Sell Differential, 6-Match VRF, 7-Match Rate,
    # 8-High Bid Price, 9-High Bid Volume, 10-High Bid Amount,
    # 11-Low Ask Price, 12-Low Ask Volume, 13-Low Ask Amount,
    # 14-Spread, 15-Market Price, 16-24hr Volume
    # 17-Buy Length, 18-Buy Selected Length, 19-Buy Length Time,
    # 20-Sell Length, 21-Sell Selected Length, 22-Sell Length Time,
    # 23-Match Length, 24-Match Selected Length, 25-Match Selected Time
    if log_active == True:
        with open(log_file, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([datetime.datetime.now(), "{}".format(user_interval), "{:.2f}".format(buy_volrateflow), "{:.2f}".format(sell_volrateflow),
                                 "{:.2f}".format(buysell_differential), "{:.2f}".format(match_volrateflow), "{:.2f}".format(match_rate),
                                 "{:.2f}".format(high_bid), "{:.2f}".format(high_bid_vol), "{:.2f}".format(high_bid_amt),
                                 "{:.2f}".format(low_ask), "{:.2f}".format(low_ask_vol), "{:.2f}".format(low_ask_amt),
                                 "{:.2f}".format(spread), "{:.2f}".format(market_price), "{:.2f}".format(day_volume),
                                 "{}".format(buy_length), "{}".format(buy_selected_length), "{:.2f}".format(time_elapsed_buylist),
                                 "{}".format(sell_length), "{}".format(sell_selected_length), "{:.2f}".format(time_elapsed_selllist),
                                 "{}".format(match_length), "{}".format(match_selected_length), "{:.2f}".format(time_elapsed_matchlist)])
    
    time.sleep(10)
    
"""   
finally:
    wsClient.close()
    print('Websocket closed.')
"""
