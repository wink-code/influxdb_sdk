import os
from pathlib import Path
from src.influxdb.query import FluxQuery
from src.influxdb.models.flux_obj import Filter
from src.influxdb import InfluxDBSDK

# current_path = Path(__file__)
# current_dir = current_path.parent
# os.chdir(current_dir)

fluxquery = FluxQuery(bucket='temp')
# print(fluxquery)

print(fluxquery.set(obj='range',start='-7d',stop='-2h'))

# # fluxquery.set_pivot()

# print()
# print(repr(fluxquery))


""" Test the Filter class """
# filter1 = Filter()
# if filter1:
#     print('filter1 is True')
# else:
#     print('filter1 is not True')
filter2 = Filter(measurement='rooms',tags={'location':'room1'})
# if filter2:
#     print('filter2 is True')
# else:
#     print('filter2 is not True')


with InfluxDBSDK.from_config_file(f"/workspace/test/influxdb-client.toml") as client:
    query_sdk = client.query_sdk()
    fluxquery.set_filters(filter2)
    print(repr(fluxquery))
    from pprint import pprint
    # result = query_sdk.query(fluxquery,columns=["_time","_field","_value"])
    result = query_sdk.query_df(fluxquery)
    pprint(result)