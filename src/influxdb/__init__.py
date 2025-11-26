from influxdb_client import InfluxDBClient
from influxdb_client.rest import ApiException
from typing import Optional,Dict,List,Literal,Any,Iterable
import requests
from src.models.flux_obj import AggregateWindowDict, PivotDict
import tomllib
from influxdb_client.client.write_api import PointSettings
from src.influxdb.utils.generate_filters import generate_filters
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
    def _validate_auth(self):
        try:
            me = self.users_api().me()
            print("\u2713 认证成功")
        except ApiException as e:
            self.close()
            if e.status == 401:
                raise ValueError(f"\u274C Token无效！响应：{e.body}") from e
            elif e.status == 403:
                raise ValueError(f"\u274C Token对 org[{self.org}] 无权限") from e
            elif e.status == 404:
                raise ValueError(f"\u274C Org [{self.org}] 不存在") from e
            else:
                raise RuntimeError(f"\u274C 认证失败！状态码：{e.status} 响应：{e.body}") from e
        # 捕获连接拒接，超时等网络错误
        except (ConnectionRefusedError, TimeoutError) as e:
            self.close()
            raise RuntimeError(f"\u274C 连接失败：无法连接到 Influx DB服务，请检查url和服务状态。错误：{str(e)}") from e
        except requests.exceptions.RequestExceptions as e:
            self.close()
            raise RuntimeError(f"\u274C 网络请求错误：{str(e)}") from e
        except Exception as e:
            self.close()
            raise RuntimeError(f"\u274C 客户端初始化失败：{str(e)}") from e
        
    def query_df(
            self,
            bucket:str=None,
            org:str=None,
            start:str='-1h',
            stop:str='now()',
            filters:Optional[Dict[str,str|List[str]]]=None,
            aggregateWindow:Optional[AggregateWindowDict]=None,
            pivot:Optional[PivotDict]=None,
            data_frame_index:List[str]=None,
            flux_script:str=None
            ):
        """
        :param bucket: bucket name
        :param start: start time of time range, default set as '-1h', here only support the relative time and absolute time formated as ISO 8601
        :param stop: stop time of time range, default set as 'now()', rest parts like stop time
        :param filters: dictionary of filter conditions, for emxample: {"_measurement":"temperature and current of devices","device_id":4,"_field":["temperature","current"]}
        :param aggregateWindow: dict that must obey the format as "{"every":"3s", "fn":"mean","createEmpty":"true"}"
        :param flux_script: has the prioriry above other parameters, if it is None, then function execute the flux script to query.
        """
        query_client = self.query_api()

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
        

    def query(
            self,
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
        """
        :param bucket: bucket name
        :param start: start time of time range, default set as '-1h', here only support the relative time and absolute time formated as ISO 8601
        :param stop: stop time of time range, default set as 'now()', rest parts like stop time
        :param filters: dictionary of filter conditions, for emxample: {"_measurement":"temperature and current of devices","device_id":4,"_field":["temperature","current"]}
        :param aggregateWindow: dict that must obey the format as "{"every":"3s", "fn":"mean","createEmpty":"true"}"
        :param flux_script: has the prioriry above other parameters, if it is None, then function execute the flux script to query.
        """
        query_client = self.query_api()

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

    def get_meta_data(self,obj:Literal["buckets","measurements","tag_keys","tag_values","fields"],context:Optional[Dict]=None)-> List[Dict[str,Any]]:
        """
        Get InfluxDB metadata(such as buckets, measurements, tags, fields)
        
        : param obj: metadata type(buckets/measurements/tags/fields)
        : param context: context parameters(for example, it is needed for bucket and measuremet to select tags)
        : return: metadata list
        """
        # factory model
        handlers = {
            "buckets": self._get_buckets,
            "measurements": self._get_measurements,
            "tag_keys": self._get_tag_keys,
            "tag_values":self._get_tag_values,
            "fields": self._get_fields
        }

        handler = handlers.get(obj)
        if not handler:
            raise ValueError(f"data type not supported:{obj}, supporting data list:{list(handlers.keys())}")
        return handler(context)
    
    def _get_buckets(self, context:Optional[Dict]=None)-> List[str]:
        """获取所有buckets(context为空)"""
        flux_script = f'''
            buckets()
            |>keep(columns:["name"])
        '''
        return self.query(flux_script=flux_script,columns=["name"])
    
    def _get_measurements(self, context:Optional[Dict]=None)-> List[str]:
        bucket = context.get('bucket')
        if not bucket:
            raise RuntimeError("bucket parameter is required.")
        flux_script = f'''
            import "influxdata/influxdb/schema"
            schema.measurements(bucket:"{bucket}")
        '''
        return self.query(flux_script=flux_script,columns=["_value"])
        # return flux_script
    
    def _get_tag_keys(self, context:Optional[Dict]=None)-> List[str]:
        bucket = context.get('bucket')
        if not bucket:
            raise RuntimeError("key bucket is required.")
        measurement = context.get('measurement')
        flux_script = f'''
            import "influxdata/influxdb/schema"
            schema.tagKeys(bucket:"{bucket}"{f', predicate: (r)=> r._measurement == "{measurement}"' if measurement else ''})
        '''
        return self.query(flux_script=flux_script,columns=["_value"])
        # return flux_script
    
    def _get_tag_values(self,context:Optional[Dict]=None)-> List[str]:
        bucket = context.get('bucket')
        if not bucket:
            raise RuntimeError("key bucket is required.")
        measurement = context.get('measurement')
        try:
            tag_key = context["tag_key"]
        except KeyError:
            raise RuntimeError(f"tag_key is required.")
        flux_script = f'''
            import "influxdata/influxdb/schema"
            schema.tagValues(bucket:"{bucket}", tag:"{tag_key}"{f', predicate: (r)=> r._measurement == "{measurement}"' if measurement else ''})
        '''
        return self.query(flux_script=flux_script,columns=["_value"])
        # return flux_script
    
    def _get_fields(self, context:Optional[Dict])-> List[str]:
        bucket = context.get('bucket')
        measurement = context.get('measurement')
        tags: Dict = context.get('tags')
        predicate_list = []
        if measurement:
            predicate_list.append( f'r._measurement == "{measurement}"')
        if tags:
            tag_list = []
            for tag_key, tag_values in tags.items():
                if isinstance(tag_values,str):
                    tag_list.append((tag_key,tag_values))
                elif isinstance(tag_values,Iterable):
                    for tag_value in tag_values:
                        tag_list.append((tag_key,tag_value))

            predicate_tags = ' or '.join(f'r.{tag_key}=="{tag_value}"' for tag_key, tag_value in tag_list)
            predicate_list.append(predicate_tags)
        predicate = ',predicate:(r)=> '+' and '.join(predicate_list) if predicate_list else ''
        flux_script = f'''
            import "influxdata/influxdb/schema"
            schema.fieldKeys(bucket:"{bucket}"{predicate})
        '''
        return self.query(flux_script=flux_script,columns=["_value"])
        # return flux_script

    @classmethod
    def from_config_file(cls, config_file = "config.ini", debug=None, enable_gzip=False, **kwargs):
        # parent_instance = super().from_config_file(config_file, debug, enable_gzip, **kwargs)
        # url = parent_instance.url
        # token = parent_instance.token
        # org = parent_instance.org
        # return cls(url=url,token=token,org=org,**kwargs)
        with open(config_file, 'rb') as f:
            data = tomllib.load(f)
        _client_config: Dict = data.get('influx2')
        if not _client_config:
            raise KeyError(f"influx2")
        _url = _client_config.pop('url')
        try:
            _token = _client_config.pop('token')
        except KeyError as e:
            raise RuntimeError(f"`url`,`token` are required in config file. Please check your Config file:{config_file}.")
        
        _default_tags: Dict = data.get('tags')
        if _default_tags:
            for default_tag_key, default_tag_value in _default_tags.items():
                PointSettings.add_default_tag(default_tag_key,default_tag_value)
        if _url:
            return cls(url=_url,token=_token,**_client_config)
        else:
            return cls(token=_token,**_client_config)
    



