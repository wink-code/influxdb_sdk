from src.influxdb import InfluxDBSDK
import os
# os.chdir(os.path.pardir(os.path.abspath(__file__)))
current_abs_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_abs_path)
os.chdir(current_dir)
with InfluxDBSDK.from_config_file('influxdb-client.toml') as sdk:
    print(type(sdk.query_df))
    df_result = sdk.query_df(bucket="temp",org='DFMC',filters={'_measurement':'rooms','_fields':["temperature","status"]},
                                    start='-1d',pivot={"columnKey":["_field"],"row_key":["_time"],"valueColumn":"_value"},
                                    data_frame_index=["_time","_fields","_value"])
    print(df_result)