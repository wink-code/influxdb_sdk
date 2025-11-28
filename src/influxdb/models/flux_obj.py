
from typing import Literal, TypedDict, Literal, List, Dict
from dataclasses import dataclass


@dataclass
class Filter:
    measurement: str|List[str] = None
    tag: Dict[str,str] = None
    field: str|List[str] = None


    def set_measurement(self, measurement):
        self.measurement = measurement

    def set_tag(self, tag_key, tag_value):# danger 
        if self.tag is None:
            self.tag = {}
        self.tag[tag_key] = tag_value
    
    def set_field(self, field):
        self.field = field

    def __bool__(self):
        return any((self.measurement,self.tag,self.field))

    def __str__(self):
        return ('<class Filter object>'
                f'\n- measurement: [{self.measurement}]'
                f'\n- tag:        [{self.tag}]'
                f'\n- field:      [{self.field}]')

    def __repr__(self):
        if not self:
            return "filter(fn: (r)=> true)"

        filter_conditions = []
        
        if self.measurement:
            if isinstance(self.measurement, List):
                measurement_statements = (f'r._measurement == "{measurement_name}"' for measurement_name in self.measurement)
                filter_conditions.append(f'filter(fn: (r)=>{' or '.join(measurement_statements)})')
            elif isinstance(self.measurement, str):
                filter_conditions.append(f'filter(fn: (r)=>r._measurement == "{self.measurement}")')
        
        if self.tag:
            tag_statements = []
            for key, value in self.tag.items():
                if isinstance(value, str):
                    tag_statements.append(f'r.{key} == "{value}"')
                else:
                    tag_statements.append(f'r.{key} == {value}')
            filter_conditions.append(f'filter(fn: (r)=> {' or '.join(tag_statements)})')
        
        if self.field:
            if isinstance(self.field, List):
                field_statements = (f'r._field == "{key}"' for key in self.field)
                filter_conditions.append(f'filter(fn:(r)=>{' or '.join(field_statements)})')
            elif isinsance(self.field, str):
                filter_conditions.append(f'filter(fn: (r)=>r._field == "{self.field}")')

        return '\n|> '.join(filter_conditions)        


class AggregateWindowDict(TypedDict):
    every: str
    fn: Literal["mean","last","median"]
    createEmpty: Literal["true","false"]

class PivotDict(TypedDict):
    rowKey: List[Literal["_time"]]
    columnKey: List[Literal["_field"]]
    valueColumn: Literal["_value"]

if __name__ == "__main__":
    def print_aggregatewindow(aggregatewindow:AggregateWindowDict):
        print(aggregatewindow)
    def print_pivot(pivot:PivotDict):
        print(pivot)
    print_aggregatewindow({"every":"3s","fn":"mean","createEmpty":"true"})
    print_pivot({"rowKey":["_time"],"columnKey":["_field"],"valueColumn":"_value"})