import time
from datetime import datetime, timedelta
from src.influxdb import InfluxDBSDK
from influxdb_client.client.write_api import PointSettings, WriteOptions
from influxdb_client import Point
import pandas as pd
from tqdm import tqdm
from zoneinfo import ZoneInfo
from typing import Iterable

# import dotenv

# dotenv.load_dotenv()

BATCH_SIZE = 1000

print()
print('=====loading datas=====')
df = pd.read_excel(r'test/test_data/4号球6月-7月数据.xlsx',parse_dates=[1],sheet_name=3,header=0,index_col=1)
print(df.head())
df = df.drop(columns=['ID'])
columns = df.columns
print('=====loading finished=====')

print()


            

def _transfer_row_to_point(row:pd.core.series.Series, set_tags:Iterable[tuple]|tuple):
    point = Point('test')
    # add tags
    if isinstance(set_tags, list):
        for tags in set_tags:
            point.tag(*tags)
    elif isinstance(set_tags, tuple):
        point.tag(*set_tags)
    for col in columns:
        point.field(col, row[col])
    local_time = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
    utc_time = local_time
    # utc_time = local_time - timedelta(hours=8)
    point.time(utc_time, write_precision='us')
    return point


if __name__ == '__main__':
    # point_settings = PointSettings(**{'location':'London','service_id':'12'})
    set_tags = [('location','London'),('service_id','12')]
    with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml') as sdk:
        with sdk.write_api(write_options=WriteOptions(
            batch_size=BATCH_SIZE
        )) as write_api:

            points = map(lambda x:_transfer_row_to_point(x[1],set_tags=set_tags), df.iterrows())
            for point in tqdm(points,total=len(df),desc='writting points'):
                write_api.write(bucket="write-test",org='DFMC',record=point)
                # print(point) # to test
                time.sleep(.01)
                
            # 手動觸發最後一批數據寫入
            write_api.flush()
            print(f'[{datetime.now()}] All written successfully!')