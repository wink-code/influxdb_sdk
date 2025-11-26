# from src.influxdb import InfluxDBSDK
from typing import Optional, Dict, List, Any
from src.models.flux_obj import AggregateWindowDict, PivotDict
from influxdb_client.rest import ApiException
from pandas import DataFrame
from src.influxdb.utils import generate_filters

class QueryProtocol:

    def query_df(
            self: "InfluxDBSDK",
            bucket:str=None,
            org:str=None,
            start:str='-1h',
            stop:str='now()',
            filters:Optional[Dict[str,str|List[str]]]=None,
            aggregateWindow:Optional[AggregateWindowDict]=None,
            pivot:Optional[PivotDict]=None,
            data_frame_index:List[str]=None,
            flux_script:str=None
            )-> DataFrame:
       ...
    
    def query(
            self: "InfluxDBSDK",
            bucket:str=None,
            org:str=None,
            start:str='-1h',
            stop:str='now()',
            filters:Optional[Dict[str,str|List[str]]]=None,
            aggregateWindow:Optional[AggregateWindowDict]=None,
            pivot:Optional[PivotDict]=None,
            columns:List[str]=None,
            flux_script:str=None
            )->List[tuple]:
        ...


def query_impl(self:QueryProtocol, **kwargs)->List[tuple]:
    """
    :param bucket: bucket name
    :param start: start time of time range, default set as '-1h', here only support the relative time and absolute time formated as ISO 8601
    :param stop: stop time of time range, default set as 'now()', rest parts like stop time
    :param filters: dictionary of filter conditions, for emxample: {"_measurement":"temperature and current of devices","device_id":4,"_field":["temperature","current"]}
    :param aggregateWindow: dict that must obey the format as "{"every":"3s", "fn":"mean","createEmpty":"true"}"
    :param flux_script: has the prioriry above other parameters, if it is None, then function execute the flux script to query.
    """
    query_client = self.query_api()
    # bucket = kwargs.get('bucket')
    # flux_script = kwargs.get('flux_script')

    if flux_script:
        results = query_client.query(flux_script)
        results_list = results.to_values(columns=columns)
        return results_list
    
    query_list = [f'from (bucket:"{bucket}")',f'range(start:{start},stop:{stop})']
    if filters:
        query_list.append(generate_filters(filters))
    if aggregateWindow:
        query_list.append(f'aggregateWindow(every:{aggregateWindow["every"]},fn:{aggregateWindow["fn"]},createEmpty:{aggregateWindow["createEmpty"]})')
    if pivot:
        m = f'pivot(rowKey:{pivot["rowKey"]},columnKey:{pivot["columnKey"]},valueColumn:"{pivot["valueColumn"]}")'
        m = m.replace('\'','"')
        query_list.append(m)
    query = '\n|>'.join(query_list)
    # print(query)
    try:
        if columns:
            results = query_client.query(query,columns=columns)
        else:
            results = query_client.query(query,columns=["_time","_value"])
    except ApiException as e:
        if e.status == 401:
            raise RuntimeError(f"Invalid or missing InfluxDB token. Error message:{e.body}") from e
        elif e.status == 403:
            raise RuntimeError(f"Token does not have permission to query the bucket. Error message:{e.body}") from e
        elif e.status == 404:
            raise RuntimeError(f"Bucket or measurement not found.{e.body}") from e
    else:
        results_list = results.to_values()
        return results_list


def query_df_impl(self: QueryProtocol, **kwargs):
    """
        :param bucket: bucket name
        :param start: start time of time range, default set as '-1h', here only support the relative time and absolute time formated as ISO 8601
        :param stop: stop time of time range, default set as 'now()', rest parts like stop time
        :param filters: dictionary of filter conditions, for emxample: {"_measurement":"temperature and current of devices","device_id":4,"_field":["temperature","current"]}
        :param aggregateWindow: dict that must obey the format as "{"every":"3s", "fn":"mean","createEmpty":"true"}"
        :param flux_script: has the prioriry above other parameters, if it is None, then function execute the flux script to query.
    """

    query_client = self.query_api()

    bucket = kwargs.get('bucket')
    flux_script = kwargs.get('flux_script')

    if flux_script:
        results = query_client.query_data_frame(flux_script,data_frame_index=['_time','_measurement','_field','_value'])
        return results
    
    query_list = [f'from (bucket:"{bucket}")',f'range(start:{start},stop:{stop})']
    if filters:
        query_list.append(generate_filters(filters))
    if aggregateWindow:
        query_list.append(f'aggregateWindow(every:{aggregateWindow["every"]},fn:{aggregateWindow["fn"]},createEmpty:{aggregateWindow["createEmpty"]})')
    if pivot:
        m = f'pivot(rowKey:{pivot["rowKey"]},columnKey:{pivot["columnKey"]},valueColumn:"{pivot["valueColumn"]}")'
        m = m.replace('\'','"')
        query_list.append(m)
    query = '\n|>'.join(query_list)
    # print(query)
    try:
        if data_frame_index:
            results = query_client.query_data_frame(query, data_frame_index=data_frame_index)
        else:
            results = query_client.query_data_frame(query, data_frame_index=['_time','_measurement','_field','_value'])# TO TEST
    except ApiException as e:
        if e.status == 401:
            raise RuntimeError(f"Invalid or missing InfluxDB token. Error message:{e.body}") from e
        elif e.status == 403:
            raise RuntimeError(f"Token does not have permission to query the bucket. Error message:{e.body}") from e
        elif e.status == 404:
            raise RuntimeError(f"Bucket or measurement not found.{e.body}") from e
    else:
        return results

def _get_variables(arg: Dict):
    