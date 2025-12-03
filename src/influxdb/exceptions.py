# src/influxdb/exceptions.py
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.rest import ApiException

class AuthenticationError(InfluxDBError):
    """ Errors related to Authentication (Token invalid, previledge doesn't meet). """

class EssentialElementsMissingError(InfluxDBError):
    """ Errros related to essential elements missing. """

class QueryError(ApiException):
    """ Errors related to Qeury """