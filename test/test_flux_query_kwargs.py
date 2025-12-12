from influxdb.models.flux_query import FluxQuery
from influxdb.models.flux_obj import Filter


def test1():
    fq = FluxQuery('bkt')
    fq.SetFilter(measurement='tm')
    print(fq)
    fq.SetAggregateWindow(every='3s',fn='mean').SetPivot(row_key=['_time'],column_key=['_field'],value_column='_value').SetLimit(n=1)
    print(fq)

def test2():
    filters = Filter().Tag('t',['v1','v2']).Measurement('m').Field('value')
    fq = FluxQuery('bkt', start='-12h',filters=filters)
    print(fq)


if __name__ == '__main__':
    test2() 