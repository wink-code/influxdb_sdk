# from src.influxdb import InfluxDBSDK
from typing import Dict, List, Literal
from pandas import DataFrame
from dataclasses import dataclass
from influxdb_client.rest import ApiException
from src.influxdb import InfluxDBSDK
from src.influxdb.models.flux_obj import AggregateWindow, Pivot, Filter
from src.influxdb.exceptions import AuthenticationError, EssentialElementsMissingError
from src.influxdb.utils.yield_statements import (yield_measurements_statement,
                                                 yield_tag_key_statement,
                                                 yield_tag_value_statement,
                                                 yield_fields_statement)

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
    filters: Filter = None
    aggregate_window: AggregateWindow = None
    pivot: Pivot = None

    def set(self,obj,*args,**kwargs):
        '''''' # to do
        return getattr(self, f'set_{obj}')(*args,**kwargs)

    def set_bucket(self,bucket):

        self.bucket = bucket
        return self
    
    def set_range(self,start,stop='now()'):
        self.start = start
        self.stop = stop
        return self

    def set_filters(self,filters:Filter):
        self.filters = filters
        return self
    
    def set_aggregate_window(self,aggregate_window: AggregateWindow):
        self.aggregate_window = aggregate_window
        return self

    def set_pivot(self,pivot: Pivot):
        self.pivot = pivot
        return self

    def __repr__(self):

        query_list = [f'from (bucket:"{self.bucket}")', f'range(start:{self.start},stop:{self.stop})',repr(self.filters)]

        if self.aggregate_window:
            query_list.append(repr(self.aggregate_window))

        if self.pivot:
            query_list.append(repr(self.pivot))
        query = '\n|> '.join(query_list)

        return query

    def __str__(self):
        return (f'<class {self.__class__.__name__} object>'
                 f'\n- bucket:           [{self.bucket}]'
                 f'\n- range:            [start:{self.start},stop:{self.stop}]'
                 f'\n- filter conditions: [\n\t\t{str(self.filters)}]'
                 f'\n- aggregateWindow:  [{self.aggregate_window}]'
                 f'\n- pivot:            [{'true' if self.pivot else 'false'}]')

    

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
            flux_script = repr(query)

        print(flux_script)   
         # debug point

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
            flux_script = repr(query)
        # print(flux_script)  # debug point

        if data_frame_index is None:
            data_frame_index = ['_time']

        return check_query_df(flux_script,data_frame_index,query_client=query_client)
        

    def query_metadata(self, 
                        obj: Literal['measurements','tag_keys','tag_values','fields'],
                        bucket:str, **context):

        obj_mapping = {
            'measurements': yield_measurements_statement,
            'tag_keys': yield_tag_key_statement,
            'tag_values': yield_tag_value_statement,
            'fields': yield_fields_statement
        }
        yield_statement = obj_mapping[obj](bucket,**context)
        print(yield_statement) # to delete, just for test

        complete_statement = _schema + yield_statement

        ## execute the querying of metadata

        return self.query(complete_statement)  # result here is just Flux Talbe List



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


_schema = 'import "influxdata/influxdb/schema"\n'