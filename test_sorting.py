import datetime
from collections import deque
import gdax
import time

buy_data = deque(maxlen=1000)
sell_data = deque(maxlen=1000)
match_data = deque(maxlen=100)


class myWebsocketClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["LTC-USD"]
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


wsClient = myWebsocketClient()
wsClient.start()

print(wsClient.url, wsClient.products)

try:
    print('Accumulating market data. Please wait...')
    while (wsClient.message_count < 1000):
        time.sleep(1)

    print('Beginning analysis.')
    while (True):
        buy_length = len(buy_data)
        buy_length_index = buy_length - 1
        sell_length = len(sell_data)
        sell_length_index = sell_length - 1
        match_length = len(match_data)
        if match_length == 0:
            match_length_index = 0
        else:
            match_length_index = match_length - 1

        print('----------------------------------------')
        print('buy_length:   ' + str(buy_length))
        print('sell_length:  ' + str(sell_length))
        print('match_length: ' + str(match_length))

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

        print('buy_avg:   ' + str(buy_avg))
        print('sell_avg:  ' + str(sell_avg))
        print('match_avg: ' + str(match_avg))
        
        time_elapsed_buy = float((buy_data[buy_length_index][0] - buy_data[0][0]).total_seconds())
        time_elapsed_sell = float((sell_data[sell_length_index][0] - sell_data[0][0]).total_seconds())
        time_elapsed_match = float((match_data[match_length_index][0] - match_data[0][0]).total_seconds())

        print('time_elapsed_buy:   ' + str(time_elapsed_buy))
        print('time_elapsed_sell:  ' + str(time_elapsed_sell))
        print('time_elapsed_match: ' + str(time_elapsed_match))
        print()

        buy_volrateflow = (60.0 * buy_avg) / time_elapsed_buy
        sell_volrateflow = (60.0 * sell_avg) / time_elapsed_sell
        buysell_differential = buy_volrateflow - sell_volrateflow
        match_volrateflow = (60.0 * match_avg) / time_elapsed_match

        print('VOLUME RATE FLOW')
        print('Buy:          ' + str(buy_volrateflow) + ' $/min')
        print('Sell:         ' + str(sell_volrateflow) + ' $/min')
        print('Differential: ' + str(buysell_differential) + ' $/min')
        print('Match:        ' + str(match_volrateflow) + ' $/min')
        print('----------------------------------------')
        print()
        
        time.sleep(10)
        
except KeyboardInterrupt:
    print('Exiting program.')
    
finally:
    wsClient.close()
    print('Websocket closed.')
