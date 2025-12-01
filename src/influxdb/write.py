from datetime import datetime

from influxdb_client.client.exceptions import InfluxDBError
from src.influxdb import InfluxDBSDK
from influxdb_client.extras import pd
from influxdb_client.domain.write_precision import WritePrecision

class WriteSDK:
    '''''' # to code
    def __init__(self, sdk: InfluxDBSDK, **kwargs):
        self._sdk = sdk
        self.point_settings = kwargs.get('point_settings') if kwargs else None
    
    def write_data_frame(self, bucket:str, data_frame: pd.DataFrame, data_frame_measurement_name: str):
        callback = BatchingCallback()
        with self._sdk.write_api(
            point_settings=self.point_settings,success_callback = callback.success,
            error_callback = callback.error,retry_callback = callback.retry) as write_client:

            start_time = datetime.now()

            print(f'writing dataframe data into bucket: {bucket}, measurement: {data_frame_measurement_name}')

            write_client.write(bucket=bucket, record=data_frame, data_frame_measurement_name=data_frame_measurement_name, write_precision='s')

        print()

        print(f'All data was written in {datetime.now()-start_time}.')

        print()



class BatchingCallback(object):
    def success(self,conf:(str,str,str),data:str):
        """Successfully written batch"""
        print(f"Written batch: {conf}")
    def error(self,conf:(str,str,str),data:str,exception:InfluxDBError):
        """Unseccessfully written batch"""
        print(f"Can't write batch: {conf},data: {data} due: {exception}")
    def retry(self,conf:(str,str,str),data:str,exception:InfluxDBError):
        """Retryable error"""
        print(f"Retryable error occurs for batch: {conf}, data: {data},retry: {exception}")
