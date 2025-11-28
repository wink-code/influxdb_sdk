from src.influxdb.models.flux_obj import Filter

filter1 = Filter()

filter1.set_tag('location','room1')
filter1.set_measurement('rooms')
filter1.set_field(['temperature','status'])
print(repr(filter1))