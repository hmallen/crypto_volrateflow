#!/usr/env python3

from collections import deque
import csv
import datetime
import dateutil.parser
import gdax
import os
import sys
import time

# Global constants
logging_threshold = 1000
logging_threshold_match = int(logging_threshold / 20)
data_length = logging_threshold * 10
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
    print('Invalid input. Exiting')
    sys.exit(1)
print()

# Backtest intervals
print('Please input desired number of backtesting intervals.')
backtest_number_raw = input('Intervals: ')
try:
    backtest_number = int(backtest_number_raw)
except:
    print('Invalid input. Exiting.')
    sys.exit(1)
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
        sys.exit(1)
    print()

backtest_intervals.sort()
delta_intervals.sort()

# Debug mode selection
print('Print data to console?')
print('1 - Yes')
print('2 - No')
debug_select_raw = input('Selection: ')
try:
    debug_select = int(debug_select_raw)
except:
    print('Invalid input. Exiting.')
    sys.exit(1)
if debug_select == 1:
    debug_mode = True
elif debug_select == 2:
    debug_mode = False
else:
    print('Invalid input. Exiting.')
    sys.exit(1)
print()

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

print('Writing header to csv file.')
for x in range(0, len(log_files)):
    with open(log_files[x], 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Date/Time', 'Market Price', '24hr Volume',
                             'High Bid', 'High Bid Vol.', 'Low Ask', 'Low Ask Vol.', 'Spread', 'Spread Vol. Diff.',
                             'Buy Avg.', 'Buy Avg. Weighted', 'Buy Avg. Exp. Weighted',
                             'Sell Avg.', 'Sell Avg. Weighted', 'Sell Avg. Exp. Weighted',
                             'Buy VRF', 'Buy VRF Weighted', 'Buy VRF Exp. Weighted',
                             'Sell VRF', 'Sell VRF Weighted', 'Sell VRF Exp. Weighted',
                             'Buy/Sell Diff.', 'Buy/Sell Diff. Weighted', 'Buy/Sell Diff. Exp. Weighted',
                             'Match Avg.', 'Match VRF', 'Match Rate (per min)', 'Match Tot. Vol.', '24hr Vol. Equivalent', 'Relative Vol. Rate'])
print()


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
        print()
        print('Closing websocket.')


# Print data to console
def display_data(data_type, backtest_index):
    if data_type == 'market':
        print()
        print('Market:       $' + "{:.2f}".format(market_price) + ' (' + "{:.2f}".format(spread) + ')')
        print('24hr Vol:      ' + "{:.2f}".format(day_volume))
        print()
        print('Low Ask:      $' + "{:.2f}".format(low_ask) + ' (' + "{:.2f}".format(low_ask_vol) + ')')
        print('High Bid:     $' + "{:.2f}".format(high_bid) + ' (' + "{:.2f}".format(high_bid_vol) + ')')
        if spread_vol_differential > 0:
            print('Vol. Diff.:   ' + '+' + "{:.2f}".format(spread_vol_differential) + ' [BUY HEAVY]')
        elif spread_vol_differential < 0:
            print('Vol. Diff.:   ' + '-' + "{:.2f}".format(abs(spread_vol_differential)) + ' [SELL HEAVY]')
        else:
            print('Vol. Diff.:    ' + "{:.2f}".format(spread_vol_differential) + ' [EVEN]')

    elif data_type == 'calc':
        print('[' + str(backtest_index) + ' min Backtest]')
        print('--- UNWEIGHTED ---')
        if buy_avg < 0:
            print('Buy Avg.:     ' + "{:.2f}".format(buy_avg))
            print('Buy VRF:      ' + "{:.2f}".format(buy_volrateflow))
        else:
            print('Buy Avg.:      ' + "{:.2f}".format(buy_avg))
            print('Buy VRF:       ' + "{:.2f}".format(buy_volrateflow))
        if sell_avg < 0:
            print('Sell Avg.:    ' + "{:.2f}".format(sell_avg))
            print('Sell VRF:     ' + "{:.2f}".format(sell_volrateflow))
        else:
            print('Sell Avg.:     ' + "{:.2f}".format(sell_avg))
            print('Sell VRF:      ' + "{:.2f}".format(sell_volrateflow))
        if buysell_differential < 0:
            print('Differential: ' + "{:.2f}".format(buysell_differential))
        else:
            print('Differential:  ' + "{:.2f}".format(buysell_differential))
        print('--- WEIGHTED ---')
        if buy_avg_weighted < 0:
            print('Buy Avg.:     ' + "{:.2f}".format(buy_avg_weighted))
            print('Buy VRF:      ' + "{:.2f}".format(buy_volrateflow_weighted))
        else:
            print('Buy Avg.:      ' + "{:.2f}".format(buy_avg_weighted))
            print('Buy VRF:       ' + "{:.2f}".format(buy_volrateflow_weighted))
        if sell_avg_weighted < 0:
            print('Sell Avg.:    ' + "{:.2f}".format(sell_avg_weighted))
            print('Sell VRF:     ' + "{:.2f}".format(sell_volrateflow_weighted))
        else:
            print('Sell Avg.:     ' + "{:.2f}".format(sell_avg_weighted))
            print('Sell VRF:      ' + "{:.2f}".format(sell_volrateflow_weighted))
        if buysell_differential_weighted < 0:
            print('Differential: ' + "{:.2f}".format(buysell_differential_weighted))
        else:
            print('Differential:  ' + "{:.2f}".format(buysell_differential_weighted))
        print('--- EXP. WEIGHTED ---')
        if buy_avg_weighted_exp < 0:
            print('Buy Avg.:     ' + "{:.2f}".format(buy_avg_weighted_exp))
            print('Buy VRF:      ' + "{:.2f}".format(buy_volrateflow_weighted_exp))
        else:
            print('Buy Avg.:      ' + "{:.2f}".format(buy_avg_weighted_exp))
            print('Buy VRF:       ' + "{:.2f}".format(buy_volrateflow_weighted_exp))
        if sell_avg_weighted_exp < 0:
            print('Sell Avg.:    ' + "{:.2f}".format(sell_avg_weighted_exp))
            print('Sell VRF:     ' + "{:.2f}".format(sell_volrateflow_weighted_exp))
        else:
            print('Sell Avg.:     ' + "{:.2f}".format(sell_avg_weighted_exp))
            print('Sell VRF:      ' + "{:.2f}".format(sell_volrateflow_weighted_exp))
        if buysell_differential_weighted_exp < 0:
            print('Differential: ' + "{:.2f}".format(buysell_differential_weighted_exp))
        else:
            print('Differential:  ' + "{:.2f}".format(buysell_differential_weighted_exp))
        print('--- OTHER ---')
        if match_avg < 0:
            print('Match Avg.:   ' + "{:.2f}".format(match_avg))
            print('Match VRF:    ' + "{:.2f}".format(match_volrateflow))
        else:
            print('Match Avg.:    ' + "{:.2f}".format(match_avg))
            print('Match VRF:     ' + "{:.2f}".format(match_volrateflow))
        print('Match Rate:    ' + "{:.2f}".format(match_rate) + ' matches/min')
        print('Match Vol.:    ' + "{:.2f}".format(match_tot_abs))
        print('24hr Equiv.:   ' + "{:.2f}".format(day_vol_equiv_rate))
        print('Rel. Ratio:    ' + "{:.2f}".format(match_rate_relative))
    print()


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
    try:
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

        if debug_mode == True:
            print('----------------------------------------')
            display_data('market', backtest_intervals[x])

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
            buy_tot_weighted = 0.0
            buy_tot_weighted_exp = 0.0
            sell_tot = 0.0
            sell_tot_weighted = 0.0
            sell_tot_weighted_exp = 0.0
            match_tot = 0.0
            match_tot_abs = 0.0

            # CHECK FUNCTION WITHOUT FLOAT DECLARATION
            for y in range(0, buy_selected_length):
                buy_vol = buy_data_selected[y][1]
                buy_price = buy_data_selected[y][2]
                buy_tot += buy_vol
                buy_tot_weighted += (1 - ((high_bid - buy_price) / high_bid)) * buy_vol
                buy_tot_weighted_exp += pow((1 - ((high_bid - buy_price) / high_bid)), 2) * buy_vol
            buy_avg = buy_tot / float(buy_selected_length)
            buy_avg_weighted = buy_tot_weighted / float(buy_selected_length)
            buy_avg_weighted_exp = buy_tot_weighted_exp / float(buy_selected_length)
            for y in range(0, sell_selected_length):
                sell_vol = sell_data_selected[y][1]
                sell_price = sell_data_selected[y][2]
                sell_tot += sell_vol
                sell_tot_weighted += (1 - ((sell_price - low_ask) / low_ask)) * sell_vol
                sell_tot_weighted_exp += pow((1 - ((sell_price - low_ask) / low_ask)), 2) * sell_vol
            sell_avg = sell_tot / float(sell_selected_length)
            sell_avg_weighted = sell_tot_weighted / float(sell_selected_length)
            sell_avg_weighted_exp = sell_tot_weighted_exp / float(sell_selected_length)
            for y in range(0, match_selected_length):
                match_vol = match_data_selected[y][1]
                match_tot += match_vol
                match_tot_abs += abs(match_vol)
            match_avg = match_tot / float(match_selected_length)

            # Unweighted
            buy_volrateflow = buy_avg / float(backtest_intervals[x])    # Buy volume per minute added to orderbook
            sell_volrateflow = sell_avg / float(backtest_intervals[x])  # Sell volume per minute added to orderbook
            buysell_differential = buy_volrateflow - sell_volrateflow  # Buy/sell volume rate flow differential
            # Weighted
            buy_volrateflow_weighted = buy_avg_weighted / float(backtest_intervals[x])    # Buy volume per minute added to orderbook
            sell_volrateflow_weighted = sell_avg_weighted / float(backtest_intervals[x])  # Sell volume per minute added to orderbook
            buysell_differential_weighted = buy_volrateflow_weighted - sell_volrateflow_weighted  # Buy/sell volume rate flow differential
            # Exponential Weighted
            buy_volrateflow_weighted_exp = buy_avg_weighted_exp / float(backtest_intervals[x])    # Buy volume per minute added to orderbook
            sell_volrateflow_weighted_exp = sell_avg_weighted_exp / float(backtest_intervals[x])  # Sell volume per minute added to orderbook
            buysell_differential_weighted_exp = buy_volrateflow_weighted_exp - sell_volrateflow_weighted_exp  # Buy/sell volume rate flow differential
            # Other
            match_volrateflow = match_avg / float(backtest_intervals[x])    # Match volume per minute
            match_rate = float(match_selected_length) / float(backtest_intervals[x])    # Matches per minute
            day_vol_equiv_rate = (day_volume / 1440.0) * float(backtest_intervals[x])   # Backtest interval equiv. rate for 24hr volume
            match_rate_relative = match_tot_abs / day_vol_equiv_rate

            if debug_mode == True:
                display_data('calc', backtest_intervals[x])

            # Log to csv or check if logging should be enabled
            if log_active == True:
                with open(log_files[x], 'a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow([datetime.datetime.now(), market_price, day_volume,
                                         high_bid, high_bid_vol, low_ask, low_ask_vol, spread, spread_vol_differential,
                                         buy_avg, buy_avg_weighted, buy_avg_weighted_exp,
                                         sell_avg, sell_avg_weighted, sell_avg_weighted_exp,
                                         buysell_differential, buysell_differential_weighted, buysell_differential_weighted_exp,
                                         match_avg, match_volrateflow, match_rate, match_tot_abs, day_vol_equiv_rate, match_rate_relative])

        if log_active == False:
            if buy_length >= logging_threshold and sell_length >= logging_threshold and match_length >= logging_threshold_match:
                print('Logging threshold achieved. Waiting for backtesting duration to elapse...')
                # Wait to collect enough data for backtesting intervals before beginning logging
                time_elapsed_buylist = float((buy_data[buy_length_index][0] - buy_data[0][0]).total_seconds())
                time_elapsed_buylist_min = time_elapsed_buylist / 60.0
                time_elapsed_selllist = float((sell_data[sell_length_index][0] - sell_data[0][0]).total_seconds())
                time_elapsed_selllist_min = time_elapsed_selllist / 60.0
                time_elapsed_matchlist = float((match_data[match_length_index][0] - match_data[0][0]).total_seconds())
                time_elapsed_matchlist_min = time_elapsed_matchlist / 60.0
                if debug_mode == True:
                    print('Buy Time:   ' + "{:.2f}".format(time_elapsed_buylist_min) + 'min')
                    print('Sell Time:  ' + "{:.2f}".format(time_elapsed_selllist_min) + 'min')
                    print('Match Time: ' + "{:.2f}".format(time_elapsed_matchlist_min) + 'min')
                if time_elapsed_buylist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]) and time_elapsed_selllist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]) and time_elapsed_matchlist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]):
                    log_active = True
                    print('Backtesting interval duration reached. Logging activated.')
                    
            elif debug_mode == True:
                print('Waiting to accumulate sufficient data...')
                print('>' + str(logging_threshold) + ' (buy/sell) / >' + str(logging_threshold_match) + ' (match)')
                print('Buy Length   = ' + str(buy_length))
                print('Sell Length  = ' + str(sell_length))
                print('Match Length = ' + str(match_length))
            print()
                    
        time.sleep(loop_time)

    except KeyboardInterrupt:
        wsClient.close()
        sys.exit(0)

    except:
        print()
        print('ENCOUNTERED ERROR. RETRYING IN 10 SECONDS.')
        print()
        time.sleep(10)
