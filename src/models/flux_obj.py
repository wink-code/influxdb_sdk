
from typing import Literal, TypedDict, Literal, List

class AggregateWindowDict(TypedDict):
    every: str
    fn: Literal["mean","last","median"]
    createEmpty: Literal["true","false"]

class PivotDict(TypedDict):
    rowKey: Literal["_time"]
    columnKey: Literal["_field"]
    keyValues: List[Literal["_value"]]

if __name__ == "__main__":
    def print_aggregatewindow(aggregatewindow:AggregateWindowDict):
        print(aggregatewindow)
    def print_pivot(pivot:PivotDict):
        print(pivot)
    print_aggregatewindow({"every":"3s","fn":"mean","createEmpty":"true"})
    # print_pivot({"rowKey":"_time","columnKey":"_field","keyValue":["_value"]})