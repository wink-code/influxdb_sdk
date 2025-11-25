import os
from src import InfluxDBSDK
os.chdir(os.path.dirname(os.path.abspath((__file__))))
with InfluxDBSDK.from_config_file('influxdb-client.toml') as client:
    # buckets = client.get_meta_data(obj='buckets')
    # print(buckets)

    # measurements = client.get_meta_data('measurements',context={"bucket":"temp"})
    # print(measurements)

    # tag_keys = client.get_meta_data(obj="tag_keys", context={"bucket":"temp","measurement":"temperature-in-different-rooms"})
    # print(tag_keys)

    # tag_values = client.get_meta_data(obj="tag_values", context={"bucket":"temp","measurement":"temperature-in-different-rooms","tag_key":"location"})
    # print(tag_values)

    field_keys = client.get_meta_data(obj='fields',context={"bucket":"temp","tags":{"location"}})
    
    