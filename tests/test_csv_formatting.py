import csv

log_file = 'test_file.csv'

with open(log_file, 'a', newline='') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['Date/Time', 'Market Price', '24hr Volume',
                         'High Bid', 'High Bid Volume', 'Low Ask', 'Low Ask Volume', 'Spread', 'Spread Volume Differential',
                         'Buy Average', 'Buy Average Weighted', 'Buy Average Exponential Weighted',
                         'Sell Average', 'Sell Average Weighted', 'Sell Average Exponential Weighted',
                         'Buy VRF', 'Buy VRF Weighted', 'Buy VRF Exponential Weighted',
                         'Sell VRF', 'Sell VRF Weighted', 'Sell VRF Exponential Weighted',
                         'Buy/Sell Differential', 'Buy/Sell Differential Weighted', 'Buy/Sell Differential Exponential Weighted',
                         'Match Average', 'Match VRF', 'Match Rate'])

test_string = 'Test string'
test_float_raw = 1.123
test_float = float(test_float_raw)

with open(log_file, 'a', newline='') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow([test_string, test_float])
