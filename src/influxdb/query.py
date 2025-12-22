# from src.influxdb import InfluxDBSDK
from typing import Dict, List, Literal
from pandas import DataFrame
from dataclasses import dataclass
from influxdb_client.rest import ApiException
from influxdb_client.client.query_api import QueryApi
from influxdb.models.flux_obj import AggregateWindow, Pivot, Filter
from influxdb.models.flux_query import FluxQuery
from influxdb.exceptions import AuthenticationError, EssentialElementsMissingError, QueryError
from influxdb.utils.yield_statements import (yield_measurements_statement,
                                                 yield_tag_key_statement,
                                                 yield_tag_value_statement,
                                                 yield_fields_statement)

class CompileError(QueryError):
    """complie error"""

    

class QuerySDK:
    '''Query SDK class for InfluxDB v2.x'''

    def __init__(self, query_api: QueryApi):
        self._query_api = query_api

    def query(self, 
            query: FluxQuery=None,
            columns: List[str] = None,
            flux_script: str = None
            )->List:    
        ''' 
        Query function 
        :param `FluxQuery`: query = None, a costomized class that organizes the flux scripts
        :param `list[str]`: columns = None, parameter of the columns you want to represent, 
            there are '["_time","_value","_field","_measurement"] and so on.
        :param `str`: flux_script = None, the flux script that has the priority beyond other parameters.
        :return `list`
        '''

        query_client = self._query_api

        if not flux_script:
            flux_script = str(query)

        print(f'flux script:\n{flux_script}')   # debug point

        if columns:
            results = submit_query(flux_script, query_client=query_client)
            return results.to_values(columns=columns)

        return submit_query(flux_script, query_client=query_client)


    def query_df(self,
                query: FluxQuery = None,
                data_frame_index: List[str] = None,
                flux_script: str = None
                )->List[DataFrame]|DataFrame:
        '''
        Query function
        param: `FluxQuery`: query, is the costomized class to build the flux script.
        param: `list[str]`: data_frame_index, is the data_frame's index you define to organize the table.
        param: `str`: flux_script, has the highest priority beyond other parameters.
        ''' 

        query_client = self._query_api

        if not flux_script:
            flux_script = str(query)
        # print(flux_script)  # debug point

        if data_frame_index:
            return submit_query_df(flux_script,
                                data_frame_index=data_frame_index,
                                query_client=query_client)

        return submit_query_df(flux_script,query_client=query_client)
        

    def query_metadata(self, # error
                        obj: Literal['measurements','tag_keys','tag_values','fields'],
                        bucket:str=None, **context):

        obj_mapping = {
            'measurements': yield_measurements_statement,
            'tag_keys': yield_tag_key_statement,
            'tag_values': yield_tag_value_statement,
            'fields': yield_fields_statement
        }
        yield_statement = obj_mapping[obj](bucket,**context)
        # print(yield_statement) # to delete, just for test

        complete_statement = _schema + f'\n{yield_statement}'
        print(complete_statement) # to delete, just for test

        ## execute the querying of metadata

        return self.query(flux_script=complete_statement, columns=context.get('columns',['_time','_value']))  # result here is just Flux Talbe List



def submit_query(flux_script, query_client):
    '''
    function that submit the flux script to influxdb, the validation responsibility to handover the influxdb backend.
    '''
    try:
        results = query_client.query(flux_script)
    except ApiException as e:
        if e.status == 400:
            raise CompileError(f"Wrong Flux Script, Error message:{e.body}") from e
        if e.status == 401:
            raise AuthenticationError(f"Invalid or missing InfluxDB token. Error message:{e.body}") from e
        if e.status == 403:
            raise AuthenticationError(f"Token does not have permission to query the bucket. Error message:{e.body}") from e
        if e.status == 404:
            raise EssentialElementsMissingError(f"Bucket or measurement not found.{e.body}") from e
        else:
            raise e
    else:
        return results
    
def submit_query_df(flux_script,query_client,data_frame_index=None): 
    try:
        results = query_client.query_data_frame(flux_script, data_frame_index=data_frame_index) 
    except ApiException as e:
        if e.status == 400:
            raise CompileError(f"Wrong Flux Script, Error message:{e.body}") from e
        if e.status == 401:
            raise AuthenticationError(f"Invalid or missing InfluxDB token. Error message:{e.body}") from e
        if e.status == 403:
            raise AuthenticationError(f"Token does not have permission to query the bucket. Error message:{e.body}") from e
        if e.status == 404:
            raise EssentialElementsMissingError(f"Bucket or measurement not found.{e.body}") from e
        else:
            raise e
    else:
        return results


_schema = 'import "influxdata/influxdb/schema"'