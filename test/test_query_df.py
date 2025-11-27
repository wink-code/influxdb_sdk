from src.influxdb import InfluxDBSDK
from src.influxdb.query import FluxQuery
import os
# os.chdir(os.path.pardir(os.path.abspath(__file__)))
current_abs_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_abs_path)
os.chdir(current_dir)
with InfluxDBSDK.from_config_file('influxdb-client.toml') as sdk:
    # print(type(sdk.query_df))
    query_sdk = sdk.query_sdk()
    flux_query = FluxQuery(bucket="temp",
                            filters={'_measurement':'rooms','_field':["temprature","status"]},
                            start='-2d',
                            pivot={"columnKey":["_field"],"rowKey":["_time"],"valueColumn":"_value"}
                            )
    
    # df_result = query_sdk.query_df(flux_query)

    # import pandas as pd                  
    # print(pd.concat(df_result)) # warning
    result = query_sdk.query(flux_query,
                        columns=["status","temprature"],
                            )
    from pprint import pprint
    pprint(result)

    # sdk.query_df()