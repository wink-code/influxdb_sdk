import time
from datetime import datetime, timedelta
from src.influxdb import InfluxDBSDK
from influxdb_client.client.write_api import PointSettings,SYNCHRONOUS
from influxdb_client import Point
import pandas as pd
from tqdm import tqdm

# import dotenv

# dotenv.load_dotenv()

MAX_BUFFER_LENGTH = 50

print()
print('=====loading datas=====')
df = pd.read_excel(r'test/test_data/4号球6月-7月数据.xlsx',parse_dates=[1],sheet_name=3,header=0,index_col=1)
print(df.head())
df = df.drop(columns=['ID'])
columns = df.columns
print('=====loading finished=====')

print()


            

def _transfer_row_to_point(row:pd.core.series.Series):
    point = Point('test')
    for col in columns:
        point.field(col, row[col])
        local_time = datetime.now()
        utc_time = local_time - timedelta(hours=8)
        point.time(utc_time, write_precision='s')
    return point


if __name__ == '__main__':
    total = 0
    point_settings = PointSettings(**{'location':'London','service_id':'12'})
    with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:
        with sdk.write_api(SYNCHRONOUS, point_settings=point_settings) as write_api:
            buffer = []
            pbar = tqdm(total=MAX_BUFFER_LENGTH, desc='buffer length')

            for i, row in df.iterrows():
                pbar.update(1)
                point = _transfer_row_to_point(row)
                # print(point) # to test
                buffer.append(point)
                time.sleep(.5)
                if len(buffer) >= MAX_BUFFER_LENGTH:
                    pbar.reset()
                    total += len(buffer)
                    print(f'[{datetime.now()}] writing buffer:({len(buffer)})...')
                    write_api.write(bucket="write-test", org="DFMC", record=buffer)
                    print(f'[{datetime.now()}] written successfully! Total:{total}.')
                    buffer.clear()