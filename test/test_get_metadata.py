import os
from src.influxdb import InfluxDBSDK
os.chdir(os.path.dirname(os.path.abspath((__file__))))
from influxdb.models.flux_obj import Filter,QueryPredicateFilter
with InfluxDBSDK.from_config_file('influxdb-client.toml') as client:
    query_sdk = client.query_sdk()
    # buckets = query_sdk.query_metadata(obj='buckets')
    # print(buckets)
    
    # measurements = query_sdk.query_metadata(bucket='temp',obj='measurements',columns=['_value'])
    # print(measurements)

    # tag_keys = query_sdk.query_metadata(obj="tag_keys", bucket='temp', columns=['_value'], measurement='rooms')
    # print(tag_keys)
    # for table in tag_keys:
    #     for row in table:
    #         print(row)

    # tag_values = query_sdk.query_metadata(obj="tag_values", bucket="temp",tag_key="location",columns=["_value"])
    # tag_values = query_sdk.query_metadata(obj="tag_values", bucket="temp",filters=PredicateFilter(measurement="rooms"),tag_key="_field")
    # tag_values = query_sdk.query_metadata(obj="tag_values", bucket="temp",filters=Filter())

    # print(tag_values)

    # field_keys = query_sdk.query_metadata(obj='fields',bucket="temp",filters=QueryPredicateFilter(tag={"location":"room1"}))
    field_keys = query_sdk.query_metadata(obj='fields',bucket="temp",filters=QueryPredicateFilter(tag={"location":["room1","room2"]},measurement="rooms"))
    # field_keys = query_sdk.query_metadata(obj='fields',context={})

    print(field_keys)
    
    