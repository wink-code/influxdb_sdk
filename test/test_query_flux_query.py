import os
from pathlib import Path
from src.influxdb.query import FluxQuery
from src.influxdb.models.flux_obj import Filter, AggregateWindow, Pivot
from src.influxdb import InfluxDBSDK

# current_path = Path(__file__)
# current_dir = current_path.parent
# os.chdir(current_dir)

# fluxquery = FluxQuery(bucket='temp')
# print(fluxquery)

# print(fluxquery.set(obj='range',start='-7d',stop='-2h'))

# # fluxquery.set_pivot()

# print()
# print(repr(fluxquery))


""" Test the Filter class """
def test_filter(i:int):
    match i:
        case 1:
            _filter = Filter()
            print(f'filter{i} ready.')
# if filter1:
#     print('filter1 is True')
# else:
#     print('filter1 is not True')
        case 2:
            _filter = Filter(measurement='rooms',tag={'location':'room1'})
            print(f'filter{i} ready.')
        case _:
            print(f'undefined case.')

# if filter2:
#     print('filter2 is True')
# else:
#     print('filter2 is not True')
    return _filter


"""
Test AggregateWindow class and Pivot class
"""
def test_aggregatewindow():
    aggregatewindow  = AggregateWindow(every='3s',fn='last',create_empty='true')
    # print(aggregatewindow)
    return aggregatewindow

def test_pivot():
    pivot = Pivot(rowKey=['_time'],columnKey=["_field","unit"],valueColumn='_value')
    # print(pivot)
    return pivot

def test_flux_query(bucket, filters:Filter, aggregate_window:AggregateWindow, pivot: Pivot):
    flux_query = FluxQuery(bucket=bucket,start='-3h',filters=filters,aggregate_window=aggregate_window,pivot=pivot)
    return flux_query

def test_query():

    with InfluxDBSDK.from_config_file(f"/workspace/test/influxdb-client.toml") as client:
        query_sdk = client.query_sdk()
        fluxquery.set_filters(filter2)
        print(repr(fluxquery))
        from pprint import pprint
        # result = query_sdk.query(fluxquery,columns=["_time","_field","_value"])
        result = query_sdk.query_df(fluxquery)
        pprint(result)


if __name__ == '__main__':
    filter2 = test_filter(2)
    pivot = test_pivot()
    aggregatewindow = test_aggregatewindow()
    pivot = test_pivot()
    flux_query = test_flux_query(bucket='temp',filters=filter2,aggregate_window=aggregatewindow,pivot=pivot)
    # print(repr(flux_query))
    print(flux_query)
    # print(filter2)

