'''
    flux_obj.py
'''
from typing import Literal, List, Dict
from dataclasses import dataclass, field as dc_field



@dataclass
class AggregateWindow:
    '''
        :param every: time interval for aggregation window, e.g. "3s","5m","1h"
        :param fn: aggregation function, support "mean","last","median"
        :param create_empty: whether to create empty windows, default is 'false'
    '''

    every: str
    fn: Literal["mean","last","median"] = 'mean'
    create_empty: Literal["true","false"] = 'false'


    def __repr__(self):
        return f'aggregateWindow(every:{self.every},fn:{self.fn},createEmpty:{self.create_empty})'



@dataclass
class Pivot:
    '''
        :param rowKey: list of row keys
        :param columnKey: list of column keys
        :param valueColumn: value column
    '''

    row_key: List[Literal["_time"]]  # to extend
    column_key: List[str]
    value_column: Literal["_value"]


    def __repr__(self):
        return ('pivot('
        f'rowKey:[{','.join(map(lambda s: f'"{s}"', self.row_key))}],'
        f'columnKey:[{','.join(map(lambda s: f'"{s}"', self.column_key))}],'
        f'valueColumn:"{self.value_column}")')



@dataclass
class Limit:
    '''
        :param n: number of points to limit
    '''

    n: int


    def __repr__(self):
        return f'limit(n:{self.n})'



@dataclass
class Filter:
    '''
        :param `str`|list[str]: measurement: measurement name or list of measurement names
        :param 'dict[str,str|list[str]]`: tag: dictionary of tag key-value pairs
        :param `str|list[str]`: field: field name or list of field names
    '''

    measurement: str|List[str] = None
    tag: Dict[str,str|List[str]] = None
    field: str|List[str] = None
    ops: str = dc_field(default='==',init=False)
    inner_joint: str = dc_field(default=' or ',init=False)
    joint: str = dc_field(default='\n|> ',init=False)
    template: str = dc_field(default='filter(fn: (r)=>{0})',init=False)
# 有一个重大的隐患， 用户输入没有强制检验，会静默传入， 导致后面的方法无法使用


    def set_measurement(self, measurement):
        'set measurement'

        self.measurement = measurement
        return self


    def set_tag(self, tag_key, tag_value):# danger
        'set tag key and value'

        if self.tag is None:
            self.tag = {}
        self.tag[tag_key] = tag_value
        return self


    def set_field(self, field):
        'set field'

        self.field = field
        return self


    def __bool__(self):
        return any((self.measurement,self.tag,self.field))


    def __repr__(self):
        return ('\n\t<class Filter object>'
                f'\n\t\t- measurement: [{self.measurement}]'
                f'\n\t\t- tag:         [{self.tag}]'
                f'\n\t\t- field:       [{self.field}]'
                '\n')


    def __str__(self):
        filter_conditions = map(self.template.format, self.compile())
        return self.joint.join(filter_conditions)


    def compile(self)-> List:
        'compile filter conditions'

        if not self:     # when no filter condition
            return ["true"]

        filter_conditions = []

        if self.measurement:
            if isinstance(self.measurement, List):
                measurement_statements = (f'r._measurement {self.ops} "{measurement_name}"'
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
                    inner_statements = (f'r.{key} {self.ops} "{ele}"'
                                        for ele in value)
                    tag_statements.append('(' + self.inner_joint.join(inner_statements) + ')')
                else:
                    tag_statements.append(f'r.{key} {self.ops} {value}')
            filter_conditions.append(" and ".join(tag_statements))

        if self.field:
            if isinstance(self.field, List):
                field_statements = (f'r._field {self.ops} "{key}"'
                                        for key in self.field)
                filter_conditions.append(self.inner_joint.join(field_statements))
            elif isinstance(self.field, str):
                filter_conditions.append(f'r._field {self.ops} "{self.field}"')

        return filter_conditions



class DeletePredicateFilter(Filter):
    'filter class that is used for delete operation'

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.joint = ' AND '
        self.template = '{}'
        self.ops = '='


class QueryPredicateFilter(Filter):
    'filter class that is used for meta query operation'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.joint = ' and '
        self.ops = ' == '
        self.template = '({})'
