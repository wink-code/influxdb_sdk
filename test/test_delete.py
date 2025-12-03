from src.influxdb import InfluxDBSDK
from src.influxdb.models.flux_obj import PredicateFilter


predicatefilter = PredicateFilter(measurement="4号球6月-7月数据",tag={'location':'London'})
# predicatefilter = PredicateFilter(measurement="4号球6月-7月数据",tag={'location':'New York'})

print(repr(predicatefilter))
with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:
    sdk.delete(bucket='write-test',start='2025-06-26T00:00:00Z',stop='2025-07-26T23:59:00Z',predicate_filter=predicatefilter)