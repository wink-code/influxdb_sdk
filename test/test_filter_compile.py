
from src.influxdb.models.flux_obj import Filter

filter1 = Filter(measurement='test',tag={'location':'New York',"unit":"k"},field=['population'],joint=' and ',template='({0})')

filter2 = Filter(measurement='temperature',tag={'machine_no':2,'location':'Beijing'},field=['quantity','height'])

# print(repr(filter1))

print(repr(filter2))