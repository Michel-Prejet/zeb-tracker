class TransitAPIError(Exception):
    """
    Exception raised when a request to the Winnipeg Transit API fails.
    """
    pass

class TransitTimeoutError(TransitAPIError):
    """
    Exception raised when a request to the Winnipeg Transit API times out.
    """
    pass

class TransitConnectionError(TransitAPIError):
    """
    Exception raised when the client cannot connect to the Winnipeg Transit API.
    """
    pass

class TransitHTTPError(TransitAPIError):
    """
    Exception raised when an HTTP error occurs when a request is sent to the
    Winnipeg Transit API.
    """
    pass

class TransitAuthenticationError(TransitHTTPError):
    """
    Exception raised when the Winnipeg Transit API rejects the API key.
    """
    pass

class TransitResponseError(TransitAPIError):
    """
    Exception raised when the Winnipeg Transit API returns unexpected or
    malformed JSON data.
    """
    pass