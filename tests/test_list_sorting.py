import datetime

test_list = [3, 1, 2, 5, 4]
print(test_list)

test_list.sort()
print(test_list)

test_deltas = [datetime.timedelta(minutes=3), datetime.timedelta(minutes=1), datetime.timedelta(minutes=2),
               datetime.timedelta(minutes=5), datetime.timedelta(minutes=4)]
print(test_deltas)

test_deltas.sort()
print(test_deltas)
