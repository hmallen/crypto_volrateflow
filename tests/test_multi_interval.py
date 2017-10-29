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
    sys.exit()
print()

# NEW CODE NEEDED
print('Please input desired backtesting time.')
user_interval_raw = input('Interval (min): ')
try:
    user_interval = int(user_interval_raw)
    delta_interval = datetime.timedelta(minutes=user_interval)
    time_start = datetime.datetime.now()
    if user_interval == 1:
        print('Using backtesting interval of 1 minute.')
    else:
        print('Using backtesting interval of ' + str(user_interval) + ' minutes.')
except:
    print('Invalid input. Exiting.')
    sys.exit()
print()

logging_threshold = 2000  # NEED TO INCREASE?
logging_threshold_match = 100  # NEED TO INCREASE?

# MAKE RELATIVE TO USER INPUT????
data_length = 20000  # NEED TO INCREASE?
data_length_match = data_length / 20  # NEED TO INCREASE?

buy_data = deque(maxlen=data_length)
sell_data = deque(maxlen=data_length)
match_data = deque(maxlen=data_length_match)

# NEW CODE NEEDED
log_datetime_raw = datetime.datetime.now()
log_datetime = log_datetime_raw.strftime('%m%d%Y-%H%M%S')
log_file = 'logs/' + log_datetime + '--' + product + '--volrateflow_log.csv'


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
    # NEED TO PLACE EVERYTHING IN A FOR LOOP
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

    buy_tot = 0.0
    sell_tot = 0.0
    match_tot = 0.0

    buy_data_selected = deque(maxlen=data_length)
    sell_data_selected = deque(maxlen=data_length)
    match_data_selected = deque(maxlen=data_length_match)

    # NEED NEW CODE
    # Parse data by time (truncate to backtesting interval)
    time_end = buy_data[buy_length_index][0] - delta_interval
    for x in range(buy_length_index, 0, -1):
        if buy_data[x][0] < time_end:
            break
        else:
            buy_data_selected.append(buy_data[x])
    buy_selected_length = len(buy_data_selected)
    buy_selected_index = buy_selected_length - 1
    for x in range(sell_length_index, 0, -1):
        if sell_data[x][0] < time_end:
            break
        else:
            sell_data_selected.append(sell_data[x])
    sell_selected_length = len(sell_data_selected)
    sell_selected_index = sell_selected_length - 1
    for x in range(match_length_index, 0, -1):
        if match_data[x][0] < time_end:
            break
        else:
            match_data_selected.append(match_data[x])
    match_selected_length = len(match_data_selected)
    match_selected_index = match_selected_length - 1
    
    for x in range(0, buy_selected_length):
        buy_tot = buy_tot + float(buy_data_selected[x][1])
    buy_avg = buy_tot / buy_selected_length
    for x in range(0, sell_selected_length):
        sell_tot = sell_tot + float(sell_data_selected[x][1])
    sell_avg = sell_tot / sell_selected_length
    for x in range(0, match_selected_length):
        match_tot = match_tot + float(match_data_selected[x][1])
    match_avg = match_tot / match_selected_length
    
    time_elapsed_buylist = float((buy_data[buy_length_index][0] - buy_data[0][0]).total_seconds())
    time_elapsed_selllist = float((sell_data[sell_length_index][0] - sell_data[0][0]).total_seconds())
    time_elapsed_matchlist = float((match_data[match_length_index][0] - match_data[0][0]).total_seconds())

    # CORRECTED
    buy_volrateflow = (60.0 * buy_avg) / float(user_interval)
    sell_volrateflow = (60.0 * sell_avg) / float(user_interval)
    buysell_differential = buy_volrateflow - float(user_interval)
    match_volrateflow = (60.0 * match_avg) / float(user_interval)
    match_rate = (60.0 * float(match_length)) / float(user_interval)

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

    # MOVE FIRST HALF TO TOP OF LOOP
    if log_active == False:
        print('Waiting to achieve data point logging threshold.')
        # Wait until sufficient quantity of data points collected
        if buy_length >= logging_threshold and sell_length >= logging_threshold and match_length >= logging_threshold_match:
            print('Logging threshold achieved. Waiting for backtesting duration to elapse.')
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

    # NEED NEW CODE
    else:
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
except KeyboardInterrupt:
    print(Exiting.)

finally:
    wsClient.close()
    print('Websocket closed.')
    sys.exit()
"""
