'''
test for flux_obj.py
'''
import unittest
from src.influxdb.models.flux_obj import AggregateWindow, Pivot, Limit, Filter

class TestFluxObj(unittest.TestCase):
    def test_aggregate_window_repr(self):
        aw = AggregateWindow(every="5m", fn="mean", create_empty="true")
        self.assertEqual(str(aw), 'aggregateWindow(every:5m,fn:mean,createEmpty:true)')

    def test_pivot_repr(self):
        pivot = Pivot(row_key=["_time"], column_key=["device_id", "location"], value_column="_value")
        self.assertEqual(str(pivot), 'pivot(rowKey:["_time"],columnKey:["device_id","location"],valueColumn:"_value")')

    def test_limit_repr(self):
        limit = Limit(n=10)
        self.assertEqual(str(limit), 'limit(n:10)')

    def test_filter_repr(self):
        filter_obj = Filter(
            measurement='temperature',
            tag={'device_id':'device_1'},
            field=['temp','humidity']
        )
        self.assertEqual(str(filter_obj), 'filter(fn:(r) => r._measurement == "temperature") \n|> filter(fn:(r) => r.device_id == "device_1") \n|> filter(fn:(r) => (r._field == "temp" or r._field == "humidity")))')