class WtAPIError(Exception):
    """
    Exception raised for any API-related error, such as a missing API key,
    a failed request, or a parsing error.
    """
    pass


class MissingAPIKeyError(WtAPIError):
    """
    Exception raised when the API key is not found in the environment.
    """
    pass


class WtClientError(WtAPIError):
    """
    Exception raised when there is a problem communicating with the Winnipeg
    Transit API.
    """
    pass

class WtTimeoutError(WtClientError):
    """
    Exception raised when a request to the Winnipeg Transit API times out.
    """
    pass

class WtConnectionError(WtClientError):
    """
    Exception raised when the client cannot connect to the Winnipeg Transit API.
    """
    pass

class WtHTTPError(WtClientError):
    """
    Exception raised when an HTTP error occurs when a request is sent to the
    Winnipeg Transit API.
    """
    def __init__(self, error_code: int):
        self.error_code = error_code

class WtAuthError(WtHTTPError):
    """
    Exception raised when the Winnipeg Transit API rejects the API key.
    """
    pass

class WtResponseError(WtClientError):
    """
    Exception raised when the Winnipeg Transit API returns unexpected or
    malformed JSON data.
    """
    pass


class WtParsingError(WtAPIError):
    """
    Exception raised when there is a problem parsing data from the Winnipeg
    Transit API.
    """
    def __init__(self, attribute_name: str, malformed_data):
        self.attribute_name = attribute_name
        self.malformed_data = str(malformed_data)

class InvalidStopTimeError(WtParsingError):
    def __init__(self, malformed_data):
        self.attribute_name = "[Stop Time]"
        self.malformed_data = malformed_data