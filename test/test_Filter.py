from src.influxdb.models.flux_obj import Filter

filter1 = Filter()

# filter1.set_tag('location',['room1','room2'])
# filter1.set_tag('another_tag',['tag_value1','tag_value2'])
# filter1.set_measurement('rooms')
# filter1.set_field(['temperature','status'])

filter1.set_tag('location',['Lodon','New York'])
print(repr(filter1))