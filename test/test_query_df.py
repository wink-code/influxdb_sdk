from src.influxdb import InfluxDBSDK
from src.influxdb.query import FluxQuery
from src.influxdb.models.flux_obj import Filter, Pivot, AggregateWindow

# os.chdir(os.path.pardir(os.path.abspath(__file__)))

with InfluxDBSDK.from_config_file('/workspace/test/influxdb-client.toml') as sdk:
    # print(type(sdk.query_df))
    query_sdk = sdk.query_sdk()
    filters = Filter(measurement='4号球6月-7月数据',tag={'location':['London','New York']},field=["给矿量设定值","给矿量检测值"])
    pivot = Pivot(columnKey=["_field",'location'],rowKey=["_time"],valueColumn="_value")
    aggregate_window = AggregateWindow(every='1h',fn='mean')
    flux_query = FluxQuery(bucket="write-test",
                            filters=filters,
                            start='2025-06-13T00:00:00Z',
                            stop='2025-07-20T00:00:00Z',
                            aggregate_window=aggregate_window,
                            pivot=pivot
                            )
    print(repr(flux_query))
    df_result = query_sdk.query_df(flux_query)
    print(df_result)

    # import pandas as pd                  
    # print(pd.concat(df_result)) # warning
    # result = query_sdk.query(flux_query,
    #                     columns=["给矿量设定值","给矿量检测值"],
    #                         )
    # from pprint import pprint
    # pprint(result)

    # sdk.query_df()