if __name__ =='__main__':
    from src.influxdb.delete import PredicateFilter
    from src.influxdb import InfluxDBSDK

    predicate = PredicateFilter(measurement=['4号球6-7月数据','4号球7-8月数据'],ops='!=',inner_joint=' and ')

    print(repr(predicate).replace("r.",""))


    with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:

        sdk.delete(bucket='online running test',start='2025-11-13T00:00:00Z',stop='2025-11-22T00:00:00Z',predicate_filter=predicate)

    # predicatefilter = PredicateFilter(measurement='test',tag={'location':'room1'},field=['temperature'])

    # predicatefilter = PredicateFilter()

    print(repr(predicate))