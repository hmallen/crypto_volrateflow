import gdax
import sys
import time

# DEBUG
product = 'BTC-USD'


class myWebsocketClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = [product]
        self.message_count = 0
    def on_message(self, msg):
        self.message_count += 1
        
        if msg["type"] == 'open':
            print('OPEN')
        elif msg["type"] == 'match':
            print('MATCH')
        elif msg["type"] == 'done' and msg["reason"] == 'canceled':
            print('CANCELED')
        
        """
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
            else:
                print('IDK WHAT'S GOING ON')
                sys.exit()
        """
    def on_close(self):
        print('Closing websocket.')


public_client = gdax.PublicClient()
wsClient = myWebsocketClient()
wsClient.start()
print(wsClient.url, wsClient.products)

while (True):
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        wsClient.close()
        sys.exit()
