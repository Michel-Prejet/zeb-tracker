class InvalidAPIStopTimeError(Exception):
    """
    Exception thrown when an ISO time read from the Winnipeg Transit API is
    improperly formatted, causing a parsing error.
    """
    pass