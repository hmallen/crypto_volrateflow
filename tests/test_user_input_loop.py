import csv
import datetime
import os
import sys

# DEBUG
product = 'BTC'
data_length = 20000
data_length_match = data_length / 100

#### TOP ####

print('Input desired number of backtesting intervals.')
backtest_number_raw = input('Intervals: ')
try:
    backtest_number = int(backtest_number_raw)
except:
    print('Invalid input. Exiting.')
    sys.exit()
print()

backtest_intervals = []

for x in range(0, backtest_number):
    print('Please input desired backtesting time.')
    user_interval_raw = input('Interval (min): ')
    try:
        user_interval = int(user_interval_raw)
        delta_interval = datetime.timedelta(minutes=user_interval)
        time_start = datetime.datetime.now()

        backtest_intervals.append(user_interval)
        
        if user_interval == 1:
            print('Using backtesting interval of 1 minute.')
        else:
            print('Using backtesting interval of ' + str(user_interval) + ' minutes.')
    except:
        print('Invalid input. Exiting.')
        sys.exit()
    print()
    
#### TOP ####

print(str(backtest_intervals) + '\n')

#### MAIN ####



#### MAIN ####

#### BOTTOM ####

dt_current = datetime.datetime.now().strftime('%m%d%Y-%H%M%S')

if not os.path.exists('logs'):
    os.makedirs('logs')

log_files = []   
for x in range(0, len(backtest_intervals)):
    log_file = 'logs/' + dt_current + '--' + product + '--' + str((x + 1)) + 'min--VRF.csv'
    log_files.append(log_file)

for x in range(0, len(log_files)):
    print(log_files[x])
    with open(log_files[x], 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['1', '2', '3'])
        
#### BOTTOM ####
