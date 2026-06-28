class BusError(Exception):
    """
    Exception thrown when any given bus attributes are invalid.
    """
    pass

class InvalidTrackingNumberError(BusError):
    pass

class InvalidYearError(BusError):
    pass

class EmptyModelError(BusError):
    pass

class DuplicateRunError(BusError):
    pass