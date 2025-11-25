from influxdb_client import InfluxDBClient
from influxdb_client.rest import ApiException
from typing import Optional,Dict,List,Literal,Any
import requests
from src.models.flux_obj import AggregateWindowDict, PivotDict

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
        
    def query(
            self,
            bucket:str,
            org:str,
            start:str='-1h',
            stop:str='now()',
            filters:Optional[Dict[str,str]]=None,
            aggregateWindow:Optional[AggregateWindowDict]=None,
            pivot:Optional[PivotDict]=None,
            data_frmae_index:List[str]=None,
            flux_script:str=None
            ):
        """
        :param bucket: bucket name
        :param start: start time of time range, default set as '-1h', here only support the relative time and absolute time formated as ISO 8601
        :param stop: stop time of time range, default set as 'now()', rest parts like stop time
        :param filters: dictionary of filter conditions, for emxample: {"_measurement":"temperature and current of devices","device_id":4,"_field":["temperature","current"]}
        :param aggregateWindow: dict that must obey the format as "{"every":"3s", "fn":"mean","createEmpty":"true"}"
        :prama flux_script: has the prioriry above other parameters, if it is None, then function execute the flux script to query.
        """
        qeury_client = self.query_api()

        if flux_script:
            results = qeury_client.query_data_frame(flux_script,data_flame_index=['_time','_measurement','_field','_value'])
            return results
        
        query_list = [f'from (bucket:"{bucket}")',f'range(start:{start},stop:{stop})']
        if filters:
            query_list.append(_generate_filters(filters))
        if aggregateWindow:
            query_list.append(f'aggregateWindow(every:{aggregateWindow["every"]},fn:{aggregateWindow["fn"]},createEmpty:{aggregateWindow["createEmpty"]})')
        if pivot:
            m = f'pivot(rowKey:{pivot["rowKey"]},columnKey:{pivot["columnKey"]},valueColumn:"{pivot["valueColumn"]}")'
            m = m.replace('\'','"')
            query_list.append(m)
        query = '\n|>'.join(query_list)
        # print(query)
        try:
            if data_frmae_index:
                results = qeury_client.query_data_frame(query, data_frame_index=data_frmae_index)
            else:
                results = qeury_client.query_data_frame(query, data_frame_index=['_time','_measurement','_field','_value'])
        except ApiException as e:
            if e.status == 401:
                raise RuntimeError(f"Invalid or missing InfluxDB token. Error message:{e.body}") from e
            elif e.status == 403:
                raise RuntimeError(f"Token does not have permission to query the bucket. Error message:{e.body}") from e
            elif e.status == 404:
                raise RuntimeError(f"Bucket or measurement not found.{e.body}") from e
        else:
            return results
        

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
        try:
            return handler(context)
        except ApiException as e:
            raise #
        except Exception as e:
            raise RuntimeError(f"获取{obj}时发生错误：{str(e)}") from e
    
    def _get_buckets(self, context:Optional[Dict]=None)-> List[Dict[str,Any]]:
        """获取所有buckets(context为空)"""
        flux_script = f'''
            buckets()
            |>keep(columns:["name"])
        '''
        return self.query(flux_script=flux_script)
    
    def _get_measurements(self, context:Optional[Dict]=None)-> List[Dict[str,Any]]:
        bucket = context.get('bucket')
        if not bucket:
            raise RuntimeError("bucket parameter is required.")
        flux_script = f'''
            import "influxdata/influxdb/schema"
            schema.measurements(bucket:"{bucket}")
        '''
        return self.query(flux_script=flux_script)
        # return flux_script
    
    def _get_tag_keys(self, context:Optional[Dict]=None):
        bucket = context.get('bucket')
        measurement = context.get('measurement')
        flux_script = f'''
            import "influxdata/influxdb/schema"
            schema.tagKeys(bucket:"{bucket}{f', predicate: (r)=> r._measurement == "{measurement}"' if measurement else ''})
        '''
        return self.query(flux_script=flux_script)
        # return flux_script
    
    def _get_tag_values(self,context:Optional[Dict]=None):
        bucket = context.get('bucket')
        measurement = context.get('measurement')
        try:
            tag_key = context["tag_key"]
        except KeyError:
            raise RuntimeError(f"tag_key is required.")
        flux_script = f'''
            import "influxdata/influxdb/schema"
            schema.tagValues(bucket:"{bucket}", tag:"{tag_key}"{f', predicate: (r)=> r._measurement == "{measurement}"' if measurement else ''})
        '''
        # return self.query(flux_script=flux_script)
        return flux_script
    
    def _get_fields(self, context:Optional[Dict]):
        bucket = context.get('bucket')
        measurement = context.get('measurement')
        tags: Dict = context.get('tags')
        predicate_list = []
        if measurement:
            predicate_list.append( f'r._measurement == "{measurement}"')
        if tags:
            predicate_tags = ' or '.join(f'{tag_key}=={tag_value}' for tag_key, tag_value in tags.items())
            predicate_list.append(predicate_tags)
        predicate = ','+' and '.join(predicate_list)
        flux_script = f'''
            import "influxdata/influxdb/schema"
            schema.fieldKeys(bucket:"{bucket}"{predicate})
        '''
        # return self.query(flux_script=flux_script)

    @classmethod
    def from_config_file(cls, config_file = "config.ini", debug=None, enable_gzip=False, **kwargs):
        parent_instance = super().from_config_file(config_file, debug, enable_gzip, **kwargs)
        url = parent_instance.url
        token = parent_instance.token
        org = parent_instance.org
        return cls(url=url,token=token,org=org,**kwargs)
        
def _generate_filters(
            filters:Dict[str,str|List[str]], 
            )->str:
    # 如果筛选条件为空，则返回全部
    if not filters:
        return "fn: (r)=> true"
    filter_conditions = []
    def _handle_list(key):
        if isinstance(filters[key],list):
            # 单独处理
            # values = filters.pop(key)
            return f" filter(fn: (r)=> {' or '.join(f'r.{key} == "{ele}"' for ele in filters[key])})"
    for key, value in filters.items():
        # 处理字符串（需加引号）和数值（直接放进去）
        if isinstance(value, str):
            filter_conditions.append(f'filter(fn: (r)=> r.{key} == "{value}")')
        elif isinstance(value,list):
            filter_conditions.append(_handle_list(key))
        else:
            filter_conditions.append(f'r.{key} == {value}')
    
    return '\n|>'.join(filter_conditions)


