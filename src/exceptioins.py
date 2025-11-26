# src/influxdb/exceptions.py

class InfluxDBError(Exception):
    """ Basic Exception class """

class AuthenticationError(InfluxDBError):
    """ Errors related to Authentication (Token invalid, previledge doesn't meet.) """

class QueryError(InfluxDBError):
    """ Errors related to Qeury """