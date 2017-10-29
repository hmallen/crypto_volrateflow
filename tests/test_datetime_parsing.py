import datetime
import dateutil.parser

dt_string = '2017-10-29T19:59:12.737000Z'
dt_new = dateutil.parser.parse(dt_string)

print(dt_new)
