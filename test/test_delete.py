from src.influxdb import InfluxDBSDK
from src.influxdb.models.flux_obj import DeletePredicateFilter

def delete1():
    predicatefilter = DeletePredicateFilter(measurement="4号球6月-7月数据",tag={'location':'New_York'})
    # predicatefilter = PredicateFilter(measurement="4号球6月-7月数据",tag={'location':'New York'})

    print(repr(predicatefilter))

    with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:
        sdk.delete(bucket='write-test',start='2025-06-26T00:00:00Z',stop='2025-07-26T23:59:00Z',predicate_filter=predicatefilter)

def delete2():
    predicatefilter = DeletePredicateFilter(measurement="test")
    with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:
        sdk.delete(bucket='write-test',start='2025-12-03T12:00:00Z',stop='2025-12-04T06:46:00Z',predicate_filter=predicatefilter)

if __name__ == '__main__':
    delete2()