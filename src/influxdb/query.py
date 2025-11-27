# from src.influxdb import InfluxDBSDK
from typing import Dict, List
from pandas import DataFrame
from dataclasses import dataclass
from influxdb_client.rest import ApiException
from src.influxdb import InfluxDBSDK
from src.models.flux_obj import AggregateWindowDict, PivotDict
from src.influxdb.utils.generate_filters import generate_filters
from src.influxdb.exceptions import AuthenticationError, EssentialElementsMissingError

@dataclass
class FluxQuery:
    """
        :param bucket: bucket name
        :param start: start time of time range, default set as '-1h', here only support the relative time and absolute time formated as ISO 8601
        :param stop: stop time of time range, default set as 'now()', rest parts like stop time
        :param filters: dictionary of filter conditions, for emxample: {"_measurement":"temperature and current of devices","device_id":4,"_field":["temperature","current"]}
        :param aggregateWindow: dict that must obey the format as "{"every":"3s", "fn":"mean","createEmpty":"true"}"
        :param flux_script: has the prioriry above other parameters, if it is None, then function execute the flux script to query.
        """ # to add the parameters
    bucket: str
    start: str = '-1h'
    stop: str = 'now()'
    filters: Dict[str,str|List[str]] = None
    aggregate_window: AggregateWindowDict = None
    pivot: PivotDict = None,


    def __str__(self):
    
        query_list = [f'from (bucket:"{self.bucket}")', f'range(start:{self.start},stop:{self.stop})']
        if self.filters:
            query_list.append(generate_filters(self.filters))
        aggregateWindow = self.aggregate_window
        if aggregateWindow:
            query_list.append(f'aggregateWindow(every:{aggregateWindow["every"]},fn:{aggregateWindow["fn"]},createEmpty:{aggregateWindow["createEmpty"]})')
        pivot = self.pivot
        if pivot:
            m = f'pivot(rowKey:{pivot["rowKey"]},columnKey:{pivot["columnKey"]},valueColumn:"{pivot["valueColumn"]}")'
            m = m.replace('\'','"')
            query_list.append(m)
        query = '\n|>'.join(query_list)
        return query

class QuerySDK:
    def __init__(self, sdk:InfluxDBSDK):
        self._sdk = sdk

    def query(self, 
            query: FluxQuery,
            columns: List[str] = None,
            flux_script: str = None
            )->List:    
        ''' '''     # to fill the doc string

        query_client = self._sdk.query_api()

        if not flux_script:
            flux_script = str(query)

        # print(flux_script)    # debug point

        if columns is None:
            columns = ['_time','_field','_value']

        return check_query(flux_script,columns,query_client=query_client)


    def query_df(self,
                query: FluxQuery,
                data_frame_index: List[str] = None,
                flux_script: str = None
                )->List[DataFrame]|DataFrame:
        ''' '''   # to fill the doc string

        query_client = self._sdk.query_api()

        if not flux_script:
            flux_script = str(query)
        # print(flux_script)  # debug point

        if data_frame_index is None:
            data_frame_index = ['_time']

        return check_query_df(flux_script,data_frame_index,query_client=query_client)
        

def check_query(flux_script,columns,query_client):
    try:
        results = query_client.query(flux_script)
    except ApiException as e:
        if e.status == 401:
            raise AuthenticationError(f"Invalid or missing InfluxDB token. Error message:{e.body}") from e
        if e.status == 403:
            raise AuthenticationError(f"Token does not have permission to query the bucket. Error message:{e.body}") from e
        if e.status == 404:
            raise EssentialElementsMissingError(f"Bucket or measurement not found.{e.body}") from e
    else:
        results_list = results.to_values(columns=columns)
        return results_list
    
def check_query_df(flux_script,data_frame_index,query_client):
    try:
        results = query_client.query_data_frame(flux_script, data_frame_index=data_frame_index)
    except ApiException as e:
        if e.status == 401:
            raise AuthenticationError(f"Invalid or missing InfluxDB token. Error message:{e.body}") from e
        if e.status == 403:
            raise AuthenticationError(f"Token does not have permission to query the bucket. Error message:{e.body}") from e
        if e.status == 404:
            raise EssentialElementsMissingError(f"Bucket or measurement not found.{e.body}") from e
    else:
        return results