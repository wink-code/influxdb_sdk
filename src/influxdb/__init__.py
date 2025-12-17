from typing import Optional,Dict
import requests
import tomllib
import os
import logging
from logging import getLogger
import dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.rest import ApiException
# from influxdb_client.client.write_api import PointSettings
# from pandas import DataFrame
# from src.influxdb.utils.chain import chain
from src.influxdb.exceptions import InfluxDBError, AuthenticationError, EssentialElementsMissingError
from src.influxdb.models.flux_obj import DeletePredicateFilter
from src.influxdb.utils.time_set import is_relative_time, get_relative_time, TimeZone

# from influxdb_client.client.write_api import WriteOptions

logging.basicConfig(level=logging.WARNING)
logger = getLogger(__name__)
handler = logging.FileHandler('influxdb_sdk.log',encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger_init = logger.getChild("influxdb.__init__")
init_handler = logging.StreamHandler()
init_formatter = logging.Formatter('%(message)s')
init_handler.setFormatter(init_formatter)
logger_init.addHandler(init_handler)
logger_init.setLevel(logging.INFO)
logger_init.propagate = False


__all__ = ["InfluxDBSDK"]
class InfluxDBSDK(InfluxDBClient):
    def __init__(
            self,
            url:str,
            org:Optional[str],
            token:str,
            **kwargs
            )->None:
        """
        :param url:str = 'http://influxdb-dev:8086' , the influxdb service host url
        :param org:str = None, represent the org of the influxdb client
        :param token:str = None, authorize to the influxdb client
        """
        logger_init.info("开始连接 InfluxDB 服务, 地址：{}".format(url))
        if not all((url,token,org)):
            logger.error(f"\u274C 客户端初始化失败 - url, token and org are required!")
            raise ValueError("Token and url are required!")

        super().__init__(url,token,org=org,**kwargs)
        # 初始化时自动校验
        try:
            self._validate_auth()
            logger_init.info("\u2713 客户端初始化成功 - [url: {}, org: {}]".format(url,org))
        except:
            logger_init.error("\u274C 客户端初始化失败 - [url: {}, org: {}]".format(url,org))
            raise InfluxDBError("Client initialization failed!")



    def _validate_auth(self):
        try:
            me = self.users_api().me()
            logger_init.info("\u2713 认证成功 - [current username: {}, id: {}]".format(me.name, me.id))
            self.me = me
        except ApiException as e:
            self.close()
            logger.error("\u274C 认证失败 - 状态码：{} 响应：{}".format(e.status, e.body))
            if e.status == 401:
                raise AuthenticationError(f"\u274C Token无效！响应：{e.body}") from e
            if e.status == 403:
                raise AuthenticationError(f"\u274C Token对 org[{self.org}] 无权限") from e
            if e.status == 404:
                raise EssentialElementsMissingError(f"\u274C Org [{self.org}] 不存在") from e
            raise InfluxDBError(f"\u274C 认证失败！状态码：{e.status} 响应：{e.body}") from e

        # 捕获连接拒接，超时等网络错误
        except (ConnectionRefusedError, TimeoutError) as e:
            logger.error("\u274C 连接失败：无法连接到 Influx DB服务，请检查url和服务状态。错误：{}".format(str(e)))
            self.close()
            raise RuntimeError(f"\u274C 连接失败：无法连接到 Influx DB服务，请检查url和服务状态。错误：{str(e)}") from e

        except requests.exceptions.RequestException as e:
            logger.error("\u274C 网络请求错误：{}".format(str(e)))
            self.close()
            raise RuntimeError(f"\u274C 网络请求错误：{str(e)}") from e

        

    @classmethod
    def from_config_file(cls, config_file = "config.toml", 
                debug=None, enable_gzip=False, **kwargs):

        with open(config_file, 'rb') as f:
            data = tomllib.load(f)
        
        try:
            _client_config: Dict = data['influx2']
        except KeyError as e:
            logger.error(f"default key is \"influx2\", please check your Config file:{config_file}.")
            raise e


        _url = _client_config.pop('url')

        try:
            _token = _client_config.pop('token')
        except:
            logger.error("`token` missed in config file."
            " Please check your Config file:{}.".format(config_file))
            raise RuntimeError(f"`token` are required in config file."
            " Please check your Config file:{config_file}.")

        if _token.startswith('{env'):
            dotenv.load_dotenv()
            t_token = os.getenv(_token[5:-1],None)
            logger_init.info("load token from environment variable:`{}`".format(_token[5:-1])) # 开发调试信息，上线可注释
            if not t_token:
                logger_init.error("environment variable `{}` not found in system, please check the variable config.".format(_token[5:-1]))
                # raise RuntimeError(f"environment variable `{_token[5:-1]}` not found in system, please check the variable config.")
        

        return cls(url=_url,token=t_token,debug=debug,enable_gzip=enable_gzip,**_client_config)


    
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
            predicate = repr(predicate_filter).replace('r.','')
            print(predicate) # to delete, only test
    
        p_start = _process_relative_time(start)

        p_stop = _process_relative_time(stop)

        try:
            super().delete_api().delete(bucket=bucket, start=p_start, stop=p_stop, predicate=predicate)
         
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

