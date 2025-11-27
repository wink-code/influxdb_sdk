from typing import Optional,Dict,List,Literal,Any,Iterable,Callable
import requests
import tomllib
import os
from types import MethodType
from influxdb_client import InfluxDBClient
from influxdb_client.rest import ApiException
from influxdb_client.client.write_api import PointSettings
from pandas import DataFrame
from src.models.flux_obj import AggregateWindowDict, PivotDict
from src.influxdb.utils.generate_filters import generate_filters
from src.influxdb.utils.chain import chain
from src.influxdb.exceptions import InfluxDBError, AuthenticationError, EssentialElementsMissingError
# from influxdb_client.client.write_api import WriteOptions


__all__ = ["InfluxDBSDK"]
class InfluxDBSDK(InfluxDBClient):
    def __init__(
            self,
            url:str='http://influxdb-dev:8086',
            org:Optional[str]=None,
            token:str=None,
            **kwargs
            )->None:
        """
        :param url:str = 'http://influxdb-dev:8086' , the influxdb service host url
        :param org:str = None, represent the org of the influxdb client
        :param token:str = None, authorize to the influxdb client
        :param default_tags: dict, the default tags define the default key-value pairs for the points
        """
        if all((url,token,org)):
            super().__init__(url,token,org=org,**kwargs)
            # 初始化时自动校验
            self._validate_auth()
        else:
            raise ValueError("Token and url are required!")
        
        default_tags = kwargs.get("default_tags")
        if default_tags:
            for default_tag_key, default_tag_value in default_tags.items():  # TO TEST
                PointSettings.add_default_tag(default_tag_key,default_tag_value)


    def _validate_auth(self):
        try:
            me = self.users_api().me()
            print(f"\u2713 认证成功\n{me}")
        except ApiException as e:
            self.close()
            if e.status == 401:
                raise AuthenticationError(f"\u274C Token无效！响应：{e.body}") from e
            if e.status == 403:
                raise AuthenticationError(f"\u274C Token对 org[{self.org}] 无权限") from e
            if e.status == 404:
                raise EssentialElementsMissingError(f"\u274C Org [{self.org}] 不存在") from e
            raise InfluxDBError(f"\u274C 认证失败！状态码：{e.status} 响应：{e.body}") from e
        # 捕获连接拒接，超时等网络错误
        except (ConnectionRefusedError, TimeoutError) as e:
            self.close()
            raise RuntimeError(f"\u274C 连接失败：无法连接到 Influx DB服务，请检查url和服务状态。错误：{str(e)}") from e
        except requests.exceptions.RequestException as e:
            self.close()
            raise RuntimeError(f"\u274C 网络请求错误：{str(e)}") from e
        except Exception as e:
            self.close()
            raise RuntimeError(f"\u274C 客户端初始化失败：{str(e)}") from e

    @classmethod
    def from_config_file(cls, config_file = "config.toml", debug=None, enable_gzip=False, **kwargs):
        with open(config_file, 'rb') as f:
            data = tomllib.load(f)
        _client_config: Dict = data.get('influx2')
        default_tags: Dict = data.get('tags')

        if not _client_config:
            raise KeyError("influx2")
        _url = _client_config.pop('url')
        try:
            _token = _client_config.pop('token')
        except:
            raise RuntimeError(f"`url`,`token` are required in config file. Please check your Config file:{config_file}.")

        if _token.startswith('{env.'):  # TO TEST
            _token = os.getenv(_token[5:-1])
            if not _token:
                raise RuntimeError(f"environment variable `{_token[5:-1]}` not found in system, please check the variable config.")
        
        if default_tags:   # TO TEST
            for default_tag_key, default_tag_value in default_tags.items():
                PointSettings.add_default_tag(default_tag_key,default_tag_value)
        if _url:
            return cls(url=_url,token=_token,**_client_config)
        return cls(token=_token,**_client_config)
    
    def query_sdk(self):
        ''' ''' # to fill the doc string
        from src.influxdb.query import QuerySDK
        return QuerySDK(self)

    def write_sdk(self):
        ''' return WriteSDK class that support influxdb write manipulations.''' # to code

    








