from influxdb.utils.time_set import get_relative_time, TimeZone

test_list = ['-2d','4h','5m','-5d']

import time

from datetime import datetime

for test_item in test_list:
    time.sleep(1)
    print(datetime.now())
    beijing_time = get_relative_time(test_item)
    print(beijing_time.astimezone(TimeZone.UTC.value))
    print('='*20)