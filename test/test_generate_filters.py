from src.influxdb import _generate_filters


# filter_dict = {'_measurement':'temperatures in rooms','location':'room1','_field':'temperature'}
# filter_dict = {}
filter_dict = {'_measurement':'temperature and humidity in rooms','location':'room1','_field':['temperature','humidity']}
filter_part = _generate_filters(filter_dict)
print(filter_part)