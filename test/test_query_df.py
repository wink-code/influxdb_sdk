from src.influxdb import InfluxDBSDK
import os
os.chdir(os.path.pardir(os.path.abspath(__file__)))
with InfluxDBSDK.from_config_file('influxdb-client.toml') as sdk:
    sdk.query_df("temp",org='DFMC',filters={'_measurement':'rooms','_fields':["temperature","status"]},start='-3h',)