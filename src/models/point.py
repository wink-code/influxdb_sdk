

from influxdb_client.client.write_api import Point

''' 
requirement: 我需要一个数据结构, 用来作为写入数据库的数据格式, 包括但不限于:
元素:
    必须: _measurement, _fields
    次必须: tags
    可选: precision(时间戳写入精度)

功能:
    批处理可选择性
    写入数据库显式反馈(每次写入单条数据,我想得到一个从数据库服务端返回的"成功"或"失败"的反馈, 就像在influxdb ui 的 lineprotocol写入反馈那样)
    



'''
