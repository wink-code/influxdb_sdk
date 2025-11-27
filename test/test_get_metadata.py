import os
from src.influxdb import InfluxDBSDK
os.chdir(os.path.dirname(os.path.abspath((__file__))))
with InfluxDBSDK.from_config_file('influxdb-client.toml') as client:
    # buckets = client.get_meta_data(obj='buckets')
    # print(buckets)

    # measurements = client.get_meta_data('measurements',context={"bucket":"temp"})
    # print(measurements)

    # tag_keys = client.get_meta_data(obj="tag_keys", context={"bucket":"temp","measurement":"rooms"})
    # print(tag_keys)
    # for table in tag_keys:
    #     for row in table:
    #         print(row)

    # tag_values = client.get_meta_data(obj="tag_values", context={"bucket":"temp","measurement":"rooms","tag_key":"location"})
    # tag_values = client.get_meta_data(obj="tag_values", context={"bucket":"temp","measurement":"rooms","tag_key":"_field"})
    # tag_values = client.get_meta_data(obj="tag_values", context={"bucket":"temp","measurement":"rooms","tag_key":"_measurement"})

    # print(tag_values)

    # field_keys = client.get_meta_data(obj='fields',context={"bucket":"temp","tags":{"location":"room1"}})
    field_keys = client.get_meta_data(obj='fields',context={"bucket":"temp","tags":{"location":["room1","room2"]},"measurement":"rooms"})
    # field_keys = client.get_meta_data(obj='fields',context={})

    print(field_keys)
    
    