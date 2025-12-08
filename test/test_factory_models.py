from influxdb import InfluxDBSDK
from src.influxdb.models.flux_obj import QueryPredicateFilter
from src.influxdb.utils.chain import chain

with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:
    query_sdk = sdk.query_sdk()
    def query_measuements():
        statement = query_sdk.query_metadata(obj='measurements',bucket='write-test')
        print(statement)
    def query_tag_keys():
        statement = query_sdk.query_metadata(obj='tag_keys',bucket='write-test',measurement='test')
    def query_tag_values():
        statement = query_sdk.query_metadata(obj='tag_values',bucket='write-test',tag_key='location')
    def query_fields_keys():
        statement = query_sdk.query_metadata(obj='fields',bucket='write-test',filters=QueryPredicateFilter(measurement='test',tag={'location':['London','New York']}))
        return statement
    result = query_fields_keys()
    print(list(chain(result)))