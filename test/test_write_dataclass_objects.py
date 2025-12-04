import time
from datetime import datetime, timedelta
from src.influxdb import InfluxDBSDK
from influxdb_client.client.write_api import PointSettings, WriteOptions
from influxdb_client import Point
import pandas as pd
from tqdm import tqdm

# import dotenv

# dotenv.load_dotenv()

BATCH_SIZE = 5000

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
    point.time(utc_time, write_precision='us')
    return point


if __name__ == '__main__':
    point_settings = PointSettings(**{'location':'London','service_id':'12'})
    with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:
        with sdk.write_api(write_options=WriteOptions(
            batch_size=BATCH_SIZE
        ), point_settings=point_settings) as write_api:

            points = map(lambda x:_transfer_row_to_point(x[1]),df.iterrows())
            for point in tqdm(points,total=len(df),desc='writting points'):
                write_api.write(bucket="write-test",org='DFMC',record=point)
                # print(point) # to test
                # time.sleep(.01)
                
            # 手動觸發最後一批數據寫入
            write_api.flush()
            print(f'[{datetime.now()}] All written successfully!')