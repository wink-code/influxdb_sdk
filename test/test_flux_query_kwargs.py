from influxdb.models.flux_query import FluxQuery
from influxdb.models.flux_obj import Filter


def test1():
    fq = FluxQuery('bkt')
    fq.set_filter(measurement='tm')
    print(fq)
    fq.set_aggregate_window(every='3s',fn='mean').set_pivot(row_key=['_time'],column_key=['_field'],value_column='_value').set_limit(n=1)
    print(fq)

def test2():
    filters = Filter().set_tag('t',['v1','v2']).set_measurement('m').set_field('value')
    fq = FluxQuery('bkt', start='-12h',filters=filters)
    fq.set_range('-8h','-1h')
    print(vars(fq))
    print()
    print(fq)


if __name__ == '__main__':
    test2() 