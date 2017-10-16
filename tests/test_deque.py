from collections import deque
import gdax
import time

d = deque(maxlen=10)


class myWebsocketClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["LTC-USD"]
        self.message_count = 0
        self.deque_count = 0
        print("Lets count the messages!")
    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            print ("Message type:", msg["type"], 
                   "\t@ {:.3f}".format(float(msg["price"])))
            if msg["type"] == 'received':
                self.deque_count += 1
                d.append(self.deque_count)
                print('Deque Count: ' + str(self.deque_count))
    def on_close(self):
        print(d)
        print("-- Goodbye! --")


wsClient = myWebsocketClient()
wsClient.start()

print(wsClient.url, wsClient.products)

while (wsClient.message_count < 250):
    print ("\nmessage_count =", "{} \n".format(wsClient.message_count))
    time.sleep(1)
wsClient.close()
