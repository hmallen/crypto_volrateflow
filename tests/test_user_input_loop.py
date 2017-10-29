import csv
import datetime
import os
import sys

# DEBUG
product = 'BTC'
data_length = 20000
data_length_match = data_length / 100

#### TOP ####

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

dt_current = datetime.datetime.now().strftime('%m%d%Y-%H%M%S')

if not os.path.exists('logs'):
    os.makedirs('logs')

log_files = []   
for x in range(0, len(backtest_intervals)):
    log_file = 'logs/' + dt_current + '--' + product + '--' + str(backtest_intervals[x]) + 'min--VRF.csv'
    log_files.append(log_file)
    
#### TOP ####

#print(str(backtest_intervals) + '\n')

#### MAIN ####

if log_active == False:
    print('Waiting to achieve data point logging threshold.')
    # Wait until sufficient quantity of data points collected
    if buy_length >= logging_threshold and sell_length >= logging_threshold and match_length >= logging_threshold_match:
        print('Logging threshold achieved. Waiting for backtesting duration to elapse.')
        # Wait to collect data for user selected duration before beginning
        time_elapsed_buylist_min = time_elapsed_buylist / 60.0
        time_elapsed_selllist_min = time_elapsed_selllist / 60.0
        time_elapsed_matchlist_min = time_elapsed_matchlist / 60.0
        if time_elapsed_buylist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]) and time_elapsed_selllist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]) and time_elapsed_matchlist_min >= float(backtest_intervals[(len(backtest_intervals) - 1)]):
            log_active = True
            print('Backtesting interval duration reached. Logging activated.')
    print()

#### MAIN ####

#### BOTTOM ####

# DONT NEED FOR LOOP WHEN WHOLE MAIN LOOP IS HANDLED WITH FOR
for x in range(0, len(log_files)):
    print(log_files[x])
    # ONLY NEED CODE BELOW
    with open(log_files[x], 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['1', '2', '3'])    # REPLACE THIS WITH REAL CODE
        
#### BOTTOM ####
