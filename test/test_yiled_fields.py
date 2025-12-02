from influxdb.utils.yield_statements import *
from influxdb.models.flux_obj import Filter

filters = Filter(measurement='test-measurement-name',tag={'location':['London','New York'],'state':'working'},field='field_value')
fields_statement = yield_fields_statement('my-bucket',filters)
# print(fields_statement)

filter2 = Filter(measurement='4号球6月-7月数据',tag={'location':['New York','London']},field=['旋流器沉砂浓度','旋流器沉砂干矿量'])
print(repr(filter2))