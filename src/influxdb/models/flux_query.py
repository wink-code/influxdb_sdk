from dataclasses import dataclass, field
from typing import List, Dict, Literal, Optional
from src.influxdb.models.flux_obj import Filter, AggregateWindow, Pivot, Limit

ATTR_CLASS_MAP = {
    "filter": Filter,
    "aggregate_window": AggregateWindow,
    "pivot": Pivot,
    "limit": Limit
}

@dataclass
class FluxQuery:
    """
        :param bucket: bucket name
        :param start: start time of time range, default set as '-1h', here only support the relative time and absolute time formated as ISO 8601
        :param stop: stop time of time range, default set as 'now()', rest parts like stop time
        :param filters: dictionary of filter conditions, for emxample: {"_measurement":"temperature and current of devices","device_id":4,"_field":["temperature","current"]}
        :param aggregateWindow: dict that must obey the format as "{"every":"3s", "fn":"mean","createEmpty":"true"}"
        :param flux_script: has the prioriry above other parameters, if it is None, then function execute the flux script to query.
        """ 
    bucket: str
    start: str = '-1h'
    stop: str = 'now()'
    filters: Filter = field(default_factory=Filter)
    aggregate_window: AggregateWindow = None
    pivot: Pivot = None
    limit: Limit = None


    def SetBucket(self,bucket):

        self.bucket = bucket
        return self
    
    def SetRange(self,start,stop='now()'): # 这里是否会有一个时间转换的问题？主要是不确定influxdb内部是将相对时间的now()以本地时间还是utc时间为基础
        self.start = start
        self.stop = stop
        return self
    
    # def set_attribute(self, attr_name: str, value=None, **kwargs):
    #     """
    #     通用属性设置方法
    #     :param attr_name: str, 属性名(如"filters","aggregate_window","pivot","limit")
    #     :param value: 已实例化的对象
    #     :param kwargs: 用于实例化对象的关键字参数
    #     """
    #     if attr_name not in ATTR_CLASS_MAP:
    #         raise ValueError(f"不支持的属性: {attr_name}")
        
    #     target_class = ATTR_CLASS_MAP[attr_name]
        
    #     if value is None:
    #         setattr(self, attr_name, target_class(**kwargs))
    #     else:
    #         setattr(self, attr_name, value)
        
    #     return self
    # def SetFilter(self, filters:Filter=None, **kwargs):
    #     return self.set_attribute("filter", filters, **kwargs)

    def SetFilter(self,filters:Filter=None, **kwargs): # 也可以传这个自定义的类对象，但是构建过程放入业务逻辑里面
        if self.filters is None:
            self.filters = Filter(**kwargs)
        else:
            self.filters = filters
        return self

    
    def SetAggregateWindow(self,aggregate_window: AggregateWindow=None, **kwargs): # !
        if self.aggregate_window is None:
            self.aggregate_window = AggregateWindow(**kwargs)
        else:
            self.aggregate_window = aggregate_window
        return self

    def SetPivot(self,pivot: Pivot=None, **kwargs): # !
        if self.pivot is None:
            self.pivot = Pivot(**kwargs)    
        else:
            self.pivot = pivot
        return self

    def SetLimit(self,limit: Limit=None, **kwargs): # !
        if self.limit is None:
            self.limit = Limit(**kwargs)
        else:
            self.limit = limit
        return self

    def __str__(self):

        query_list = [f'from (bucket:"{self.bucket}")', 
                      f'range(start:{self.start},stop:{self.stop})',
                      repr(self.filters)]

        if self.aggregate_window:
            query_list.append(repr(self.aggregate_window))

        if self.pivot:
            query_list.append(repr(self.pivot))
        query = '\n|> '.join(query_list)

        if self.limit:
            query += f'\n|> {repr(self.limit)}'
        return query

    def __repr__(self):
        return (f'<class {self.__class__.__name__} object>'
                 f'\n- bucket:           [{self.bucket}]'
                 f'\n- range:            [start:{self.start},stop:{self.stop}]'
                 f'\n- filter conditions: [\n\t\t{repr(self.filters)}]'
                 f'\n- aggregateWindow:  [{self.aggregate_window}]'
                 f'\n- pivot:            [{'true' if self.pivot else 'false'}]'
                 f'\n- limit:            [{self.limit}]'
                )