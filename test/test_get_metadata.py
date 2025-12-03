import os
from src.influxdb import InfluxDBSDK
os.chdir(os.path.dirname(os.path.abspath((__file__))))
from influxdb.models.flux_obj import Filter
with InfluxDBSDK.from_config_file('influxdb-client.toml') as client:
    # buckets = client.get_meta_data(obj='buckets')
    # print(buckets)
    query_sdk = client.query_sdk()
    
    # measurements = query_sdk.query_metadata(bucket='temp',obj='measurements',columns=['_value'])
    # print(measurements)

    # tag_keys = query_sdk.query_metadata(obj="tag_keys", bucket='temp', columns=['_value'], measurement='rooms')
    # print(tag_keys)
    # for table in tag_keys:
    #     for row in table:
    #         print(row)

    # tag_values = query_sdk.query_metadata(obj="tag_values", bucket="temp",tag_key="location",columns=["_value"])
    # tag_values = client.get_meta_data(obj="tag_values", context={"bucket":"temp","measurement":"rooms","tag_key":"_field"})
    tag_values = query_sdk.query_metadata(obj="tag_values", bucket="temp",filters=Filter())

    print(tag_values)

    # field_keys = client.get_meta_data(obj='fields',context={"bucket":"temp","tags":{"location":"room1"}})
    # field_keys = client.get_meta_data(obj='fields',context={"bucket":"temp","tags":{"location":["room1","room2"]},"measurement":"rooms"})
    # field_keys = client.get_meta_data(obj='fields',context={})

    # print(field_keys)
    
    