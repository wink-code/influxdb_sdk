
from typing import Literal, Literal, List, Dict
from dataclasses import dataclass

@dataclass
class AggregateWindow:
    every: str
    fn: Literal["mean","last","median"] = 'mean'
    create_empty: Literal["true","false"] = 'false'

    def __repr__(self):
        return f'aggregateWindow(every:{self.every},fn:{self.fn},createEmpty:{self.create_empty})'

@dataclass
class Pivot:
    rowKey: List[Literal["_time"]]  # to extend
    columnKey: List[str]
    valueColumn: Literal["_value"]

    def __repr__(self):
        return ('pivot('
        f'rowKey:[{','.join(map(lambda s: f'"{s}"', self.rowKey))}],'
        f'columnKey:[{','.join(map(lambda s: f'"{s}"', self.columnKey))}],'
        f'valueColumn:"{self.valueColumn}")')




@dataclass
class Filter:
    measurement: str|List[str] = None
    tag: Dict[str,str|List[str]] = None
    field: str|List[str] = None
    ops: str = '=='
    inner_joint: str = ' or '
    joint: str = '\n|> '
    template: str = 'filter(fn: (r)=>{0})'


    def set_measurement(self, measurement):
        self.measurement = measurement
        return self

    def set_tag(self, tag_key, tag_value):# danger 
        if self.tag is None:
            self.tag = {}
        self.tag[tag_key] = tag_value
        return self
    
    def set_field(self, field):
        self.field = field
        return self

    def __bool__(self):
        return any((self.measurement,self.tag,self.field))

    def __str__(self):
        return ('<class Filter object>'
                f'\n\t\t- measurement: [{self.measurement}]'
                f'\n\t\t- tag:         [{self.tag}]'
                f'\n\t\t- field:       [{self.field}]'
                '\n\t\t      ')

    def __repr__(self):
        if not self:
            return self.template.format("true")

        filter_conditions = map(lambda s: self.template.format(s), self.compile())

        return self.joint.join(filter_conditions)

    def compile(self)->List:
        if not self:
            return "true"

        filter_conditions = []
        
        if self.measurement:
            if isinstance(self.measurement, List):
                measurement_statements = (f'r._measurement {self.ops} "{measurement_name}"' if isinstance(measurement_name,str)
                                            else f'r._measurement {self.ops} {measurement_name}'
                                            for measurement_name in self.measurement)

                filter_conditions.append(self.inner_joint.join(measurement_statements))
            elif isinstance(self.measurement, str):
                filter_conditions.append(f'r._measurement {self.ops} "{self.measurement}"')
        
        if self.tag:
            tag_statements = []
            for key, value in self.tag.items():
                if isinstance(value, str):
                    tag_statements.append(f'r.{key} {self.ops} "{value}"')
                elif isinstance(value, List):
                    inner_statements = (f'r.{key} {self.ops} "{ele}"' if isinstance(ele, str)
                                        else f'r.{key} {self.ops} {ele}'
                                        for ele in value)

                    tag_statements.append(self.inner_joint.join(inner_statements))
                else:
                    tag_statements.append(f'r.{key} {self.ops} {value}')
            filter_conditions.append(" and ".join(tag_statements))
        
        if self.field:
            if isinstance(self.field, List):
                field_statements = (f'r._field {self.ops} "{key}"' if isinstance(key, str)
                                        else f'r._field {self.ops} {key}'                
                                        for key in self.field)
                                        
                filter_conditions.append(self.inner_joint.join(field_statements))
            elif isinstance(self.field, str):
                filter_conditions.append(f'r._field {self.ops} "{self.field}"')

        return filter_conditions

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


class DeletePredicateFilter(Filter):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.joint = ' AND '
        self.template = '{}'
        self.ops = '='


class QueryPredicateFilter(Filter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.joint = ' and '
        self.ops = ' == '
        self.template = '({})'

