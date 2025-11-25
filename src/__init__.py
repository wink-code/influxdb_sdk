from influxdb_client import InfluxDBClient
from influxdb_client.rest import ApiException
import os
from typing import Optional,Dict,List,Literal
import requests
from .models.flux_obj import AggregateWindowDict, PivotDict


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
        qeury_client = self.query_api

        if flux_script:
            results = qeury_client.query_data_frame(query_flux,data_flame_index=['_time','_measurement','_field','_value'])
            return results
        
        query_list = [f'from (bucket:"{bucket}")',f'range(start:{start},stop:{stop})']
        if filters:
            query_list.append(_generate_filters(filters))
        if aggregateWindow:
            query_list.append(f'aggregateWindow(every:{aggregateWindow["every"]},fn:{aggregateWindow["fn"]},createEmpty:{aggregateWindow["createEmpty"]})')
        if pivot:
            m = f'pivot(rowKey:"{pivot["rowKey"]}",columnKey:"{pivot["columnKey"]}",columnValues:[{pivot["columnValues"]}])'
            m.replace('\.','"')
            query_list.append(m)
        query = '\n|>'.join(query_list)
        print(query)

                
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
