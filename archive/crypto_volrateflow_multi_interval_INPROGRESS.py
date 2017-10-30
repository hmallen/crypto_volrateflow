#!/usr/env python3

# TO DO:
# - Log multiple time intervals (multiple files) for testing
# - Add buy rate/sell rate (RELATIVE TO 24HR VOLUME?)
# - Plot long interval vs. short interval and look for crossover?
# - NEED TO SPLIT INTO MULTIPLE LOGS
# - NEED TO MAKE WEIGHTED AVERAGES
# - NEED TO ADD NEW AVERAGES TO DISPLAY_DATA()
# - Remove formatting from csv write (full float precision)
# - Remove references to USD. Work with crypto volume only for analysis.

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

#### NEW ####
print('Please input desired number of backtesting intervals.')
backtest_number_raw = input('Intervals: ')
try:
    backtest_number = int(backtest_number_raw)
except:
    print('Invalid input. Exiting.')
    sys.exit()
print()

backtest_intervals = []
delta_intervals = []

for x in range(0, backtest_number):
    print('Please input desired backtesting time.')
    user_interval_raw = input('Interval (min): ')
    try:
        user_interval = int(user_interval_raw)
        #time_start = datetime.datetime.now()   # IS THIS NEEDED?

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

print('Backtest Intervals: ' + str(backtest_intervals))
print('Delta Intervals:    ' + str(delta_intervals))
print()

dt_current = datetime.datetime.now().strftime('%m%d%Y-%H%M%S')

if not os.path.exists('logs'):
    os.makedirs('logs')

log_files = []   
for x in range(0, len(backtest_intervals)):
    log_file = 'logs/' + dt_current + '--' + product + '--' + str(backtest_intervals[x]) + 'min--VRF.csv'
    log_files.append(log_file)
#### NEW ####

logging_threshold = 2000  # NEED TO INCREASE?
logging_threshold_match = 100  # NEED TO INCREASE?

# MAKE RELATIVE TO USER INPUT????
data_length = 20000  # NEED TO INCREASE?
data_length_match = int(data_length / 20)  # NEED TO INCREASE?

buy_data = deque(maxlen=data_length)
sell_data = deque(maxlen=data_length)
match_data = deque(maxlen=data_length_match)


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
                order_size = float(msg["size"])
                order_price = float(msg["price"])
                order_tot = order_size * order_price
                if msg_side == 'buy':
                    buy_data.append((msg_time, order_tot, order_size, order_price))
                elif msg_side == 'sell':
                    sell_data.append((msg_time, order_tot, order_size, order_price))
            elif msg_type == 'done' and msg["reason"] == 'cancelled':
                order_size = float(msg["size"])
                order_price = float(msg["price"])
                order_tot = -1.0 * order_size * order_price
                if msg_side == 'buy':
                    buy_data.append((msg_time, order_tot, order_size, order_price))
                elif msg_side == 'sell':
                    sell_data.append((msg_time, order_tot, order_size, order_price))
            elif msg_type == 'match':
                order_size = float(msg["size"])
                order_price = float(msg["price"])
                order_tot = order_size * order_price
                if msg_side == 'buy':
                    match_data.append((msg_time, order_tot, order_size, order_price))
                elif msg_side == 'sell':
                    match_data.append((msg_time, (-1.0 * order_tot), order_size, order_price))
            elif msg_type == 'change':
                order_size = float(msg["size"])
                order_price = float(msg["price"])
                order_tot = order_size * order_price
                print('---- CHANGE ----')
    def on_close(self):
        print('Closing websocket.')


# NEW CODE NEEDED
def display_data(): # NEED TO UPDATE WITH NEW VARIABLES
    print('----------------------------------------')
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
    print('Low Ask:           $' + "{:.2f}".format(low_ask) + ' - ' + "{:.2f}".format(low_ask_vol) + ' - ' + 'Total: $' + "{:.2f}".format(low_ask_amt))
    print('High Bid:          $' + "{:.2f}".format(high_bid) + ' - ' + "{:.2f}".format(high_bid_vol) + ' - ' + 'Total: $' + "{:.2f}".format(high_bid_amt))
    print('Market Price:      $' + "{:.2f}".format(market_price) + ' ($' + "{:.2f}".format(spread) + ') - 24hr Volume: ' + "{:.2f}".format(day_volume))
    print('----------------------------------------')
    print()


# NEW CODE NEEDED
def display_data_simple(backtest_index): # NEED TO UPDATE WITH NEW VARIABLES
    print('VOLUME RATE FLOW ' + str(backtest_index) + ' min backtest')
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


public_client = gdax.PublicClient()

wsClient = myWebsocketClient()
wsClient.start()

print(wsClient.url, wsClient.products)

log_active = False

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

while (True):
    product_book = public_client.get_product_order_book(product, level=1)
    product_ticker = public_client.get_product_ticker(product_id=product)

    for x in range(0, len(backtest_intervals)):
        buy_length = len(buy_data)
        buy_length_index = buy_length - 1
        sell_length = len(sell_data)
        sell_length_index = sell_length - 1
        match_length = len(match_data)
        match_length_index = match_length - 1

        """
        # NEEDED?
        if match_length == 0:
            match_length_index = 0
        else:
            match_length_index = match_length - 1
        """

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

        print('buy_selected_length   = ' + str(buy_selected_length))
        print('sell_selected_length  = ' + str(sell_selected_length))
        print('match_selected_length = ' + str(match_selected_length))

        buy_tot = 0.0
        sell_tot = 0.0
        match_tot = 0.0
        
        for y in range(0, buy_selected_length):
            buy_tot = buy_tot + float(buy_data_selected[y][1])
        #buy_tot = buy_tot / float(backtest_intervals[x])
        buy_avg = buy_tot / float(buy_selected_length)
        for y in range(0, sell_selected_length):
            sell_tot = sell_tot + float(sell_data_selected[y][1])
        #sell_tot = sell_tot / float(backtest_intervals[x])
        sell_avg = sell_tot / float(sell_selected_length)
        for y in range(0, match_selected_length):
            match_tot = match_tot + float(match_data_selected[y][1])
        #match_tot = match_tot / float(backtest_intervals[x])
        match_avg = match_tot / float(match_selected_length)

        # CORRECTED
        """
        buy_volrateflow = (60.0 * buy_avg) / float(backtest_intervals[x])
        sell_volrateflow = (60.0 * sell_avg) / float(backtest_intervals[x])
        buysell_differential = buy_volrateflow - sell_volrateflow
        match_volrateflow = (60.0 * match_avg) / float(backtest_intervals[x])
        match_rate = (60.0 * float(match_length)) / float(backtest_intervals[x])
        """

        print('backtest_intervals[x] = ' + str(backtest_intervals[x]))
        print('buy_avg   = ' + str(buy_avg))
        print('sell_avg  = ' + str(sell_avg))
        print('match_avg = ' + str(match_avg))
        buy_volrateflow = buy_avg / float(backtest_intervals[x])
        sell_volrateflow = sell_avg / float(backtest_intervals[x])
        buysell_differential = buy_volrateflow - sell_volrateflow
        match_volrateflow = match_avg / float(backtest_intervals[x])
        match_rate = float(match_selected_length) / float(backtest_intervals[x])

        high_bid = float(product_book['bids'][0][0])
        high_bid_vol = float(product_book['bids'][0][1])
        high_bid_amt = high_bid * high_bid_vol
        low_ask = float(product_book['asks'][0][0])
        low_ask_vol = float(product_book['asks'][0][1])
        low_ask_amt = low_ask * low_ask_vol
        spread = low_ask - high_bid

        market_price = float(product_ticker['price'])
        day_volume = float(product_ticker['volume'])

        time_elapsed_buylist = float((buy_data[buy_length_index][0] - buy_data[0][0]).total_seconds())
        time_elapsed_selllist = float((sell_data[sell_length_index][0] - sell_data[0][0]).total_seconds())
        time_elapsed_matchlist = float((match_data[match_length_index][0] - match_data[0][0]).total_seconds())

        #display_data()
        display_data_simple(backtest_intervals[x])

        # MOVE FIRST HALF TO TOP OF LOOP
        if log_active == True:
            with open(log_files[x], 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([datetime.datetime.now(), "{}".format(user_interval), "{:.2f}".format(buy_volrateflow), "{:.2f}".format(sell_volrateflow),
                                     "{:.2f}".format(buysell_differential), "{:.2f}".format(match_volrateflow), "{:.2f}".format(match_rate),
                                     "{:.2f}".format(high_bid), "{:.2f}".format(high_bid_vol), "{:.2f}".format(high_bid_amt),
                                     "{:.2f}".format(low_ask), "{:.2f}".format(low_ask_vol), "{:.2f}".format(low_ask_amt),
                                     "{:.2f}".format(spread), "{:.2f}".format(market_price), "{:.2f}".format(day_volume),
                                     "{}".format(buy_length), "{}".format(buy_selected_length), "{:.2f}".format(time_elapsed_buylist),
                                     "{}".format(sell_length), "{}".format(sell_selected_length), "{:.2f}".format(time_elapsed_selllist),
                                     "{}".format(match_length), "{}".format(match_selected_length), "{:.2f}".format(time_elapsed_matchlist)])
        
    #display_data() # PUT DISPLAY DATA HERE?

    if log_active == False:
        print('Buy Time:   ' + str(time_elapsed_buylist))
        print('Sell Time:  ' + str(time_elapsed_selllist))
        print('Match Time: ' + str(time_elapsed_matchlist))
        print('Buy Length:   ' + str(buy_length))
        print('Sell Length:  ' + str(sell_length))
        print('Match Length: ' + str(match_length))
        print()
        print('Waiting to achieve data point logging threshold.')
        # Wait until sufficient quantity of data points collected
        if buy_length >= logging_threshold and sell_length >= logging_threshold and match_length >= logging_threshold_match:
            print('Logging threshold achieved. Waiting for backtesting duration to elapse.')
            # Wait to collect data for user selected duration before beginning
            time_elapsed_buylist_min = time_elapsed_buylist / 60.0
            print(time_elapsed_buylist_min)
            time_elapsed_selllist_min = time_elapsed_selllist / 60.0
            print(time_elapsed_selllist_min)
            time_elapsed_matchlist_min = time_elapsed_matchlist / 60.0
            print(time_elapsed_matchlist_min)
            print(backtest_intervals[(len(backtest_intervals) - 1)])
            if time_elapsed_buylist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]) and time_elapsed_selllist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]) and time_elapsed_matchlist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]):
                log_active = True
                print('Backtesting interval duration reached. Logging activated.')
        print()
    
    time.sleep(10)

"""
except KeyboardInterrupt:
    print(Exiting.)

finally:
    wsClient.close()
    print('Websocket closed.')
    sys.exit()
"""
