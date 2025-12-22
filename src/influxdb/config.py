from typing import Optional,Dict
import requests
import tomllib
import os
import logging

import dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.rest import ApiException
from src.influxdb.models.flux_obj import DeletePredicateFilter
from src.influxdb.utils.time_set import is_relative_time, get_relative_time, TimeZone




# Set up logging
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('influxdb_sdk.log',encoding='utf-8')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding='utf-8')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)



__all__ = ["InfluxDBConfig"]




class InfluxDBConfig:
    '''InfluxDB Config Client class, suppoert InfluxDB v2.x series.'''


    def __init__(
            self,
            url:str,
            token:str,
            org:Optional[str],
            config_file: Optional[str] = None,
            **kwargs
            )->None:
        """
        :param url:str, the influxdb service host url
        :param org:str, represent the org of the influxdb client
        :param token:str, authorize to the influxdb client
        :param config_file: str, the config file path of influxdb client, default key is `influx2`.
        """
        if config_file:
            with open(config_file, 'rb') as f:
                data = tomllib.load(f)
            _client_config: Dict = data['influx2']
            try:
                self.url = _client_config.pop('url')
                self.org = _client_config.pop('org', None)
                self.token = _client_config.pop('token')
                self.kwargs = _client_config
            except KeyError as e:
                logger.error("`token`,`url`,`org` missed in config file."
                             " Please check your Config file: %s." % config_file)
                raise EssentialElementsMissingError(f"`token` are required in config file."
                             " Please check your Config file: {config_file}.") from e
            if self.token.startswith('{env'):
                dotenv.load_dotenv()
                t_token = os.getenv(self.token[5:-1], None)
                logger.info("load token from environment variable:`%s`", self.token[5:-1]) # 开发调试信息，上线可注释
                if not t_token:
                    logger.error("environment variable `%s` not found in system, please check the variable config.", self.token[5:-1])
                    # raise RuntimeError(f"environment variable `{self.token[5:-1]}` not found in system, please check the variable config.")
                else:
                    self.token = t_token
        else:
            self.url = url
            self.org = org
            self.token = token
            self.kwargs = kwargs





    def query_sdk(self):
        ''' return QuerySDK class object that support influx query. ''' 
        from src.influxdb.query import QuerySDK
        return QuerySDK(self)



    def write_sdk(self,point_settings=None):
        ''' return WriteSDK class that support influxdb write manipulations.''' 
        from src.influxdb.write import WriteSDK
        return WriteSDK(self,point_settings=point_settings)



    def delete(self, bucket:str, start:str, stop:str, predicate_filter: DeletePredicateFilter):
        ''' 
        Delete the points that satisfy the conditions of parameters.
        param str: bucket, the bucket where points will be deleted.
        param str: start, start time of the deleted points, formation could be relative deltatime, like '-1h', 
        or absolute deltatime, like '2025-11-30T12:00:00Z'.
        param str: stop, stop time of the deleted points, formation is the same as the `start` parameter.
        param PredicateFilter: predicate, is a self-defined class that is to organize the filtering conditions, 
        in which you are expected to initialize the class object
        like `predicate = PredicateFilter(measurement:str|list='your-bucket',tag:dict={'locatioin':'New York'},
        field:str|list=['temperature','humulity']).
        '''
        if not predicate_filter:
            predicate = None
        else:
            predicate = str(predicate_filter).replace('r.','')
            # print(predicate) # to delete, only test
    
        p_start = _process_relative_time(start)

        p_stop = _process_relative_time(stop)

        try:
            self.delete_api.delete(bucket=bucket, start=p_start, stop=p_stop, predicate=predicate)
         
        except ApiException as e:
            print(f"failed to delte:bucket:{bucket},start:{start},stop:{stop}"
                                f"\n                {predicate}"
                                f"\n                error:{str(e)}")
        else:
            print(f'NO Errors! [Action: delete]'
                    f'\nstart:{start},stop:{stop}')




def _process_relative_time(r_time: str):
    if is_relative_time(r_time):
        abs_start = get_relative_time(r_time).astimezone(TimeZone.UTC.value)
        return abs_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    return r_time

