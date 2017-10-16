# Time delta testing

import datetime
from collections import deque
import time

date_list = deque(maxlen=100)
date_list_new = deque(maxlen=100)

current_datetime = datetime.datetime.now()
delta = datetime.timedelta(seconds=5)
new_time = current_datetime - delta

for x in range(1, 11):
    now = datetime.datetime.now()
    date_list.append((x, now))
    time.sleep(1)

list_length = len(date_list)
print('Length: ' + str(list_length))

for x in range(0, list_length):
    print(date_list[x])

time.sleep(2)

#time_range = datetime.datetime.now() - delta
time_range = date_list[(list_length - 1)][1] - delta
for x in range((list_length - 1), 0, -1):
    if date_list[x][1] < time_range:
        print('BREAK')
        break
    else:
        print('APPEND')
        date_list_new.append(date_list[x])

list_length_new = len(date_list_new)
print('Length: ' + str(list_length_new))

for x in range(0, list_length_new):
    print(date_list_new[x])
