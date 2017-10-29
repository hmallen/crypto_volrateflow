#!/usr/env python3

from collections import deque
import csv
import datetime
import dateutil.parser
import gdax
import os
import sys
import time

debug_mode = True

# Global constants
log_threshold = 2000
log_thresh_match = int(log_threshold / 20)
data_length = log_threshold * 10
data_length_match = int(data_length / 20)
loop_time = 10  # Time delay between loops (seconds)

# Global variables/lists
backtest_intervals = []
delta_intervals = []
buy_data = deque(maxlen=data_length)
sell_data = deque(maxlen=data_length)
match_data = deque(maxlen=data_length_match)

# COLLECT USER INPUT

# Product selection
print()
print('1: BTC-USD')
print('2: LTC-USD')
print('3: ETH-USD')
print()

user_product = input('Plese choose product: ')
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
    sys.exit()
print()

# Backtest intervals
print('Please input desired number of backtesting intervals.')
backtest_number_raw = input('Intervals: ')
try:
    backtest_number = int(backtest_number_raw)
except:
    print('Invalid input. Exiting.')
    sys.exit()
print()

for x in range(0, backtest_number):
    print('Please input desired backtesting time.')
    user_interval_raw = input('Interval (min): ')
    try:
        user_interval = int(user_interval_raw)

        backtest_intervals.append(user_interval)
        delta_intervals.append(datetime.timedelta(minutes=user_interval))
        
        if user_interval == 1:
            print('Using backtesting interval of 1 minute.')
        else:
            print('Using backtesting interval of ' + str(user_interval) + ' minutes.')
    except:
        print('Invalid input. Exiting.')
        sys.exit()
    print()

backtest_intervals.sort()
delta_intervals.sort()

dt_current = datetime.datetime.now().strftime('%m%d%Y-%H%M%S')

if not os.path.exists('logs'):
    print('Log directory not found. Creating...')
    os.makedirs('logs')
else:
    print('Log directory found.')

log_files = []   
for x in range(0, len(backtest_intervals)):
    log_file = 'logs/' + dt_current + '--' + product + '--' + str(backtest_intervals[x]) + 'min--VRF.csv'
    log_files.append(log_file)


class myWebsocketClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = 'wss://ws-feed.gdax.com/'
        self.products = [product]
        self.message_count = 0
        
    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            msg_time = dateutil.parser.parse(msg['time'])
            msg_type = msg['type']
            msg_side = msg['side']
            
            if msg_type == 'received':
                order_size = float(msg['size'])
                order_price = float(msg['price'])
                if msg_side == 'buy':
                    buy_data.append((msg_time, order_size, order_price))
                elif msg_side == 'sell':
                    sell_data.append((msg_time, order_size, order_price))
                    
            elif msg_type == 'done' and msg['reason'] == 'cancelled':
                order_size = float(msg['size']) * -1.0  # Negative to remove from book
                order_price = float(msg['price'])
                if msg_side == 'buy':
                    buy_data.append((msg_time, order_size, order_price))
                elif msg_side == 'sell':
                    sell_data.append((msg_time, order_size, order_price))
                    
            elif msg_type == 'match':
                order_size = float(msg['size'])
                order_price = float(msg['price'])
                if msg_side == 'buy':
                    match_data.append((msg_time, order_size, order_price))
                elif msg_side == 'sell':
                    match_data.append((msg_time, (order_size * -1.0), order_price))  # Negative for sell to offset buy matches
                    
            elif msg_type == 'change':
                print('---- CHANGE ----')
                order_size = float(msg['size'])
                order_price = float(msg['price'])
                print('---- CHANGE ----')
                
    def on_close(self):
        print('Closing websocket.')


# Print data to console
def display_data(data_type):
    if data_type == 'market':
        print('Stuff & Things')

    elif data_type == 'calc':
        print('Stuff & Things')


# Websocket start-up
public_client = gdax.PublicClient()
wsClient = myWebsocketClient()
wsClient.start()

# Accumulate some market data before attempting analysis
print('Accumulating market data. Please wait...')
while (wsClient.message_count < 1000):
    time.sleep(1)
print('Waiting for all data lists to populate. Please wait...')
while (True):
    buy_length = len(buy_data)
    sell_length = len(sell_data)
    match_length = len(match_data)
    if buy_length > 0 and sell_length > 0 and match_length > 0:
        break
    time.sleep(1)
print('Beginning analysis. Logging will start when backtesting interval reached.')
print()

log_active = False  # False until enough data acquired to satisfy backtesting interval
while (True):
    # Get current lvl1 orderbook
    product_book = public_client.get_product_order_book(product, level=1)
    high_bid = float(product_book['bids'][0][0])
    high_bid_vol = float(product_book['bids'][0][1])
    low_ask = float(product_book['asks'][0][0])
    low_ask_vol = float(product_book['asks'][0][1])
    spread = low_ask - high_bid
    spread_vol_differential = high_bid_vol - low_ask_vol

    # Get current ticker
    product_ticker = public_client.get_product_ticker(product_id=product)
    market_price = float(product_ticker['price'])
    day_volume = float(product_ticker['volume'])

    display_data('market')

    for x in range(0, len(backtest_intervals)):
        buy_length = len(buy_data)
        buy_length_index = buy_length - 1
        sell_length = len(sell_data)
        sell_length_index = sell_length - 1
        match_length = len(match_data)
        match_length_index = match_length - 1

        buy_data_selected = deque(maxlen=data_length)
        sell_data_selected = deque(maxlen=data_length)
        match_data_selected = deque(maxlen=data_length_match)

        # Parse data by time (truncate to backtesting interval)
        time_end = buy_data[buy_length_index][0] - delta_intervals[x]
        for y in range(buy_length_index, 0, -1):
            if buy_data[y][0] < time_end:
                break
            else:
                buy_data_selected.append(buy_data[y])
        buy_selected_length = len(buy_data_selected)
        buy_selected_index = buy_selected_length - 1
        for y in range(sell_length_index, 0, -1):
            if sell_data[y][0] < time_end:
                break
            else:
                sell_data_selected.append(sell_data[y])
        sell_selected_length = len(sell_data_selected)
        sell_selected_index = sell_selected_length - 1
        for y in range(match_length_index, 0, -1):
            if match_data[y][0] < time_end:
                break
            else:
                match_data_selected.append(match_data[y])
        match_selected_length = len(match_data_selected)
        match_selected_index = match_selected_length - 1

        # Perform calculations
        buy_tot = 0.0
        sell_tot = 0.0
        match_tot = 0.0

        for y in range(0, buy_selected_length):
            buy_tot += float(buy_data_selected[y][1])
        buy_avg = buy_tot / float(buy_selected_length)
        for y in range(0, sell_selected_length):
            sell_tot += float(sell_data_selected[y][1])
        sell_avg = sell_tot / float(sell_selected_length)
        for y in range(0, match_selected_length):
            match_tot += float(match_data_selected[y][1])
        match_avg = match_tot / float(match_selected_length)

        buy_volrateflow = buy_avg / float(backtest_intervals[x])    # Buy volume per minute added to orderbook
        sell_volrateflow = sell_avg / float(backtest_intervals[x])  # Sell volume per minute added to orderbook
        match_volrateflow = match_avg / float(backtest_intervals[x])    # Match volume per minute
        buysell_differential = buy_volrateflow - sell_volrateflow  # Buy/sell volume rate flow differential
        match_rate = float(match_selected_length) / float(backtest_intervals[x])    # Matches per minute

        if debug_mode == True:
            display_data('calc')

        # Log to csv or check if logging should be enabled
        if log_active == True:
            print('Stuff & Things')
            
        else:
            if buy_length >= logging_threshold and sell_length >= logging_threshold and match_length >= logging_threshold_match:
                print('Logging threshold achieved. Waiting for backtesting duration to elapse.')
                # Wait to collect enough data for backtesting intervals before beginning logging
                time_elapsed_buylist = float((buy_data[buy_length_index][0] - buy_data[0][0]).total_seconds())
                time_elapsed_buylist_min = time_elapsed_buylist / 60.0
                print('Buy Time:   ' + str(time_elapsed_buylist_min) + 'min')
                time_elapsed_selllist = float((sell_data[sell_length_index][0] - sell_data[0][0]).total_seconds())
                time_elapsed_selllist_min = time_elapsed_selllist / 60.0
                print('Sell Time:  ' + str(time_elapsed_selllist_min) + 'min')
                time_elapsed_matchlist = float((match_data[match_length_index][0] - match_data[0][0]).total_seconds())
                time_elapsed_matchlist_min = time_elapsed_matchlist / 60.0
                print('Match Time: ' + str(time_elapsed_matchlist_min) + 'min')
                if time_elapsed_buylist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]) and time_elapsed_selllist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]) and time_elapsed_matchlist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]):
                    log_active = True
                    print('Backtesting interval duration reached. Logging activated.')
            else:
                print('buy_selected_length   = ' + str(buy_selected_length))
                print('sell_selected_length  = ' + str(sell_selected_length))
                print('match_selected_length = ' + str(match_selected_length))
            print()

        time.sleep(loop_time)
