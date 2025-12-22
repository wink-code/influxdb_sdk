# src/influxdb/exceptions.py
from influxdb_client.rest import ApiException

class InfluxDBClientError(Exception):
    """ Base class for InfluxDB Client related errors. """

class AuthenticationError(InfluxDBClientError):
    """ Errors related to Authentication (Token invalid, previledge doesn't meet). """

class EssentialElementsMissingError(InfluxDBClientError):
    """ Errros related to essential elements missing. """

class QueryError(ApiException):
    """ Errors related to Qeury """

class SDKInitializationError(InfluxDBClientError):
    """ Errors related to SDK Initialization """