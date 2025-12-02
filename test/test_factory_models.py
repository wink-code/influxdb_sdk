from influxdb import InfluxDBSDK
from src.influxdb.models.flux_obj import Filter

with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:
    query_sdk = sdk.query_sdk()
    def query_measuements():
        statement = query_sdk.query_metadata(obj='measurements',bucket='write-test')
        print(statement)
    def query_tag_keys():
        statement = query_sdk.query_metadata(obj='tag_keys',bucket='write-test',measurement='4号球6月-7月数据')
    def query_tag_values():
        statement = query_sdk.query_metadata(obj='tag_values',bucket='write-test',tag_key='location')
    def query_fields_keys():
        statement = query_sdk.query_metadata(obj='fields',bucket='write-test',filters=Filter(measurement='4号球6月-7月数据',tag={'location':['London','New York']}))
    query_fields_keys()